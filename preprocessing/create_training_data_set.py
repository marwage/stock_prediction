import argparse
import datetime
import json
import logging
import nltk
nltk.download("vader_lexicon")
import os
import pandas as pd
import pymongo
import re
import sys
import threading
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pathlib import Path
from textblob import TextBlob
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.threads import divide_in_chunks


def start_with_threads(task,
                       sp500: list,
                       first_date: datetime.datetime,
                       last_date: datetime.datetime,
                       data_path: str):
    num_threads = 12
    sp500_chunks = list(divide_in_chunks(sp500, num_threads))

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=task,
                                  args=(sp500_chunks[i],
                                        first_date,
                                        last_date,
                                        data_path))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)
    return sp500_json["sp500"]


def clean_text(text):
    cleaned = re.sub(r"\n+", " ", text)
    cleaned = re.sub(r" {2,}", " ", cleaned)
    url_regex = r"((http|https)://)(www.)?[a-zA-Z0-9@:%._\+~#?&//=]{1,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%._\+~#?&//=]*)"
    cleaned = re.sub(url_regex, "", cleaned)
    return cleaned


def get_sentiment_textblob(text):
    text_blob = TextBlob(text)
    return (text_blob.sentiment.polarity,
            text_blob.sentiment.subjectivity)


def get_sentiment_nltk(text):
    sid = SentimentIntensityAnalyzer()
    score = sid.polarity_scores(text)
    return score

def get_relative_price_difference(day, next_day):
    stock_price_day = day["open"]
    stock_price_next_day = next_day["open"]
    return (stock_price_next_day - stock_price_day) / stock_price_day


def increase_day_one(date: datetime.datetime):
    return date + datetime.timedelta(days=1)


def get_contains_cashtag(text: str, company: str):
    match = re.search(r"\${}".format(company), text)
    if match is None:
        return 0.0
    else:
        return 1.0


def get_tweet_features(tweet: dict, company: str):
    features = dict()

    text = tweet["text"]
    use_textblob = False
    if use_textblob:
        sentiment = get_sentiment_textblob(text)
        features["sentiment_polarity"] = sentiment[0]
        features["sentiment_subjectivity"] = sentiment[1]
    else:
        sentiment = get_sentiment_nltk(text)
        features["sentiment_negative"] = sentiment["neg"]
        features["sentiment_neutral"] = sentiment["neu"]
        features["sentiment_positive"] = sentiment["pos"]
        features["sentiment_compound"] = sentiment["compound"]
    if "followers_count" in tweet["user"]:
        followers = float(tweet["user"]["followers_count"])
    else:
        followers = 0.0
    features["followers"] = followers
    if "friends_count" in tweet["user"]:
        friends = float(tweet["user"]["friends_count"])
    else:
        friends = 0.0
    features["friends"] = friends
    if "listed_count" in tweet["user"]:
        listed = float(tweet["user"]["listed_count"])
    else:
        listed = 0.0
    features["listed"] = listed
    if "favourites_count" in tweet["user"]:
        favourites = float(tweet["user"]["favourites_count"])
    else:
        favourites = 0.0
    features["user_favourites"] = favourites
    if "statuses_count" in tweet["user"]:
        statuses = float(tweet["user"]["statuses_count"])
    else:
        statuses = 0.0
    features["statuses"] = statuses
    if "retweet_count" in tweet:
        retweets = float(tweet["retweet_count"])
    else:
        retweets = 0.0
    features["retweets"] = retweets
    if "favorite_count" in tweet:
        favourites = float(tweet["favorite_count"])
    else:
        favourites = 0.0
    features["tweet_favourites"] = favourites
    features["cashtag"] = get_contains_cashtag(text, company)
    features["language"] = tweet["lang"]

    return features


def get_stocktwits_sentiment(sentiment: str):
    if sentiment is None:
        return 0.0
    elif sentiment == "Bullish":
        return 1.0
    elif sentiment == "Bearish":
        return -1.0
    else:  # error
        return None


def get_idea_features(idea: dict):
    features = dict()

    text = idea["body"]
    use_textblob = False
    if use_textblob:
        sentiment = get_sentiment_textblob(text)
        features["sentiment_polarity"] = sentiment[0]
        features["sentiment_subjectivity"] = sentiment[1]
    else:
        sentiment = get_sentiment_nltk(text)
        features["sentiment_negative"] = sentiment["neg"]
        features["sentiment_neutral"] = sentiment["neu"]
        features["sentiment_positive"] = sentiment["pos"]
        features["sentiment_compound"] = sentiment["compound"]
    features["followers"] = float(idea["user"]["followers"])
    features["following"] = float(idea["user"]["following"])
    features["ideas"] = float(idea["user"]["ideas"])
    features["watch_list"] = float(idea["user"]["watchlist_stocks_count"])
    features["user_likes"] = float(idea["user"]["like_count"])
    if "likes" in idea:
        idea_likes = float(idea["likes"]["total"])
    else:
        idea_likes = 0.0
    features["idea_likes"] = idea_likes
    if ("sentiment" in idea["entities"]
            and idea["entities"]["sentiment"] is not None
            and "basic" in idea["entities"]["sentiment"]):
        sentiment_str = idea["entities"]["sentiment"]["basic"]
    else:
        sentiment_str = None
    features["sentiment_stocktwits"] = get_stocktwits_sentiment(sentiment_str)

    return features


def get_industry(industry_str: str, mapping: pd.DataFrame):
    mapping_row = mapping[mapping["industry"] == industry_str]
    value = float(mapping_row["value"])
    return value


def get_sector(sector_str: str, mapping: pd.DataFrame):
    mapping_row = mapping[mapping["sector"] == sector_str]
    value = float(mapping_row["value"])
    return value

def parse_str_to_float(string: str):
    if string == "None":
        return 0.0
        
    return float(string)


def get_company_info(info: dict,
                     industry_mapping: pd.DataFrame,
                     sector_mappping: pd.DataFrame):
    features = dict()

    features["200DayMovingAverage"] = parse_str_to_float(info["200DayMovingAverage"])
    features["50DayMovingAverage"] = parse_str_to_float(info["50DayMovingAverage"])
    features["52WeekHigh"] = parse_str_to_float(info["52WeekHigh"])
    features["52WeekLow"] = parse_str_to_float(info["52WeekLow"])
    features["Beta"] = parse_str_to_float(info["Beta"])
    features["BookValue"] = parse_str_to_float(info["BookValue"])
    features["DilutedEPSTTM"] = parse_str_to_float(info["DilutedEPSTTM"])
    features["DividendPerShare"] = parse_str_to_float(info["DividendPerShare"])
    features["DividendYield"] = parse_str_to_float(info["DividendYield"])
    features["EBITDA"] = parse_str_to_float(info["EBITDA"])
    features["EPS"] = parse_str_to_float(info["EPS"])
    features["EVToEBITDA"] = parse_str_to_float(info["EVToEBITDA"])
    features["EVToRevenue"] = parse_str_to_float(info["EVToRevenue"])
    features["ForwardAnnualDividendRate"] = parse_str_to_float(info["ForwardAnnualDividendRate"])
    features["ForwardAnnualDividendYield"] = parse_str_to_float(info["ForwardAnnualDividendYield"])
    features["ForwardPE"] = parse_str_to_float(info["ForwardPE"])
    features["FullTimeEmployees"] = parse_str_to_float(info["FullTimeEmployees"])
    features["GrossProfitTTM"] = parse_str_to_float(info["GrossProfitTTM"])
    industry = get_industry(info["Industry"], industry_mapping)
    features["Industry"] = industry
    features["MarketCapitalization"] = parse_str_to_float(info["MarketCapitalization"])
    features["OperatingMarginTTM"] = parse_str_to_float(info["OperatingMarginTTM"])
    features["PEGRatio"] = parse_str_to_float(info["PEGRatio"])
    features["PERatio"] = parse_str_to_float(info["PERatio"])
    features["PayoutRatio"] = parse_str_to_float(info["PayoutRatio"])
    features["PercentInsiders"] = parse_str_to_float(info["PercentInsiders"])
    features["PercentInstitutions"] = parse_str_to_float(info["PercentInstitutions"])
    features["PriceToBookRatio"] = parse_str_to_float(info["PriceToBookRatio"])
    features["PriceToSalesRatioTTM"] = parse_str_to_float(info["PriceToSalesRatioTTM"])
    features["ProfitMargin"] = parse_str_to_float(info["ProfitMargin"])
    features["QuarterlyEarningsGrowthYOY"] = parse_str_to_float(info["QuarterlyEarningsGrowthYOY"])
    features["QuarterlyRevenueGrowthYOY"] = parse_str_to_float(info["QuarterlyRevenueGrowthYOY"])
    features["ReturnOnAssetsTTM"] = parse_str_to_float(info["ReturnOnAssetsTTM"])
    features["ReturnOnEquityTTM"] = parse_str_to_float(info["ReturnOnEquityTTM"])
    features["RevenuePerShareTTM"] = parse_str_to_float(info["RevenuePerShareTTM"])
    features["RevenueTTM"] = parse_str_to_float(info["RevenueTTM"])
    sector = get_sector(info["Sector"], sector_mappping)
    features["Sector"] = sector
    features["SharesFloat"] = parse_str_to_float(info["SharesFloat"])
    features["SharesOutstanding"] = parse_str_to_float(info["SharesOutstanding"])
    features["SharesShort"] = parse_str_to_float(info["SharesShort"])
    features["SharesShortPriorMonth"] = parse_str_to_float(info["SharesShortPriorMonth"])
    features["ShortPercentFloat"] = parse_str_to_float(info["ShortPercentFloat"])
    features["ShortPercentOutstanding"] = parse_str_to_float(info["ShortPercentOutstanding"])
    features["ShortRatio"] = parse_str_to_float(info["ShortRatio"])
    features["TrailingPE"] = parse_str_to_float(info["TrailingPE"])

    return features


def construct_day(client: pymongo.MongoClient,
                  company: str,
                  start_date: datetime.datetime,
                  end_date: datetime.datetime,
                  price_diff: float,
                  industry_mapping: pd.DataFrame,
                  sector_mapping: pd.DataFrame):
    trainingdataset_db = client["trainingdatasetdb"]
    twitter_db = client["twitterdb"]
    stocktwits_db = client["stocktwitsdb"]
    company_info_db = client["companyinfodb"]
    twitter_coll = twitter_db[company]
    stocktwits_coll = stocktwits_db[company]
    if False:
        data_set_coll = trainingdataset_db["Ava"]
    else:
        data_set_coll = trainingdataset_db["Bella"]
    company_info_coll = company_info_db[company]

    trading_start = datetime.datetime(start_date.year,
                                      start_date.month,
                                      start_date.day,
                                      14, 30)
    trading_start_next_day = datetime.datetime(end_date.year,
                                               end_date.month,
                                               end_date.day,
                                               14, 30)

    # Twitter
    cursor = twitter_coll.find({"date": {"$gte": trading_start,
                                         "$lt": trading_start_next_day}})

    tweets_raw = [tweet.copy() for tweet in cursor]
    num_tweets_raw = len(tweets_raw)
    if num_tweets_raw > 0:
        tweets_raw.sort(key=(lambda x: x["date"]))
        tweets = [get_tweet_features(tweet, company) for tweet in tweets_raw]
    else:
        tweets = []

    # Stocktwits
    cursor = stocktwits_coll.find({"date": {"$gte": trading_start,
                                            "$lt": trading_start_next_day}})
    ideas_raw = [idea.copy() for idea in cursor]
    num_ideas_raw = len(ideas_raw)
    if num_ideas_raw > 0:
        ideas_raw.sort(key=(lambda x: x["date"]))
        ideas = [get_idea_features(idea) for idea in ideas_raw]
    else:
        ideas = []

    # Check if there are any tweets or ideas
    if not tweets and not ideas:
        return False

    # Company Info
    info = company_info_coll.find_one({})
    if info is None:
        return False
    company_info = get_company_info(info, industry_mapping, sector_mapping)

    # create data point
    day = dict()
    day["company"] = company
    day["start"] = trading_start
    day["end"] = trading_start_next_day
    day["price_diff"] = price_diff
    day["tweets"] = tweets
    day["ideas"] = ideas
    day["company_info"] = company_info

    data_set_coll.update_one({"start": trading_start, "company": company},
                             {"$set": day},
                             upsert=True)

    return True


def create_training_data_set(companies: list,
                             first_date: datetime.datetime,
                             last_date: datetime.datetime,
                             data_path: str):
    client = pymongo.MongoClient()
    stockprice_db = client["stockpricedb"]

    industry_mapping = pd.read_csv(os.path.join(data_path, "industries.csv"))
    sector_mapping = pd.read_csv(os.path.join(data_path, "sectors.csv"))

    for company in companies:
        logging.info("%s:Get training samples", company)

        stock_price_coll = stockprice_db[company]

        # for each day
        start_date = first_date
        while start_date <= last_date:
            price_day = stock_price_coll.find_one({"date": start_date})

            if price_day is None:
                start_date = increase_day_one(start_date)
                continue

            # get next trading day
            end_date = increase_day_one(start_date)
            price_next_day = stock_price_coll.find_one({"date": end_date})
            while price_next_day is None and end_date <= last_date:
                end_date = increase_day_one(end_date)
                price_next_day = stock_price_coll.find_one({"date": end_date})

            if price_next_day is None:
                logging.debug("%s:There is no end date for start date %s",
                              company,
                              start_date)
                start_date = increase_day_one(start_date)
                continue

            price_diff = get_relative_price_difference(price_day,
                                                       price_next_day)

            created_data_point = construct_day(client,
                                               company,
                                               start_date,
                                               end_date,
                                               price_diff,
                                               industry_mapping,
                                               sector_mapping)
            if not created_data_point:
                logging.debug("%s:There are no tweets nor ideas for date %s",
                              company,
                              start_date)

            start_date = end_date


def main():
    if sys.platform == "linux":
        base_path = os.path.join(Path.home(), "stock/stock-prediction")
    else:
        path = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        base_path = os.path.join(Path.home(), path)

    data_path = os.path.join(base_path, "preprocessing/data")
    path = "preprocessing/log/create_training_data_set.log"
    logging_path = os.path.join(base_path, path)
    logging.basicConfig(
        filename=logging_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    sp500_path = os.path.join(base_path, "crawling/data/sp500.json")
    sp500 = read_sp500(sp500_path)

    first_date = datetime.datetime(2019, 6, 1)
    last_date = datetime.datetime(2021, 4, 15)

    if args.threading:
        start_with_threads(create_training_data_set,
                           sp500,
                           first_date,
                           last_date,
                           data_path)
    else:
        create_training_data_set(sp500, first_date, last_date, data_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count tweets")
    parser.add_argument("--threading", action="store_true",
                        help="Enable threading")
    args = parser.parse_args()

    main()
