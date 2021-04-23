import datetime
import json
import logging
import os
import re
import sys
from pathlib import Path
from pymongo import MongoClient
from textblob import TextBlob


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


def stocktwits_get_text(tweet):
    if "body" in tweet:
        return tweet["body"]
    elif "text" in tweet:
        return tweet["text"]
    else:
        return None


def get_sentiment(text):
    text_blob = TextBlob(text)
    return text_blob.sentiment.polarity


def get_relative_price_difference(day, next_day):
    stock_price_day = day["open"]
    stock_price_next_day = next_day["open"]
    return (stock_price_next_day - stock_price_day) / stock_price_day


def increase_day_one(date: datetime.datetime):
    return date + datetime.timedelta(days=1)


def create_training_data_set(companies: list,
                            first_date: datetime.datetime,
                            last_date: datetime.datetime):
    client = MongoClient()
    trainingdataset_db = client["trainingdatasetdb"]
    twitter_db = client["twitterdb"]
    stocktwits_db = client["stocktwitsdb"]
    stockprice_db = client["stockpricedb"]
    data_set_coll = trainingdataset_db["Ava"]

    for company in companies:
        logging.info("%s:Get training samples", company)

        twitter_coll = twitter_db[company]
        stocktwits_coll = stocktwits_db[company]
        stock_price_coll = stockprice_db[company]

        # for each day
        start = first_date
        while start <= last_date:
            stock_price_day = stock_price_coll.find_one({"date": start})

            if stock_price_day is None:
                start = increase_day_one(start)
                continue

            # get next trading day
            end = increase_day_one(start)
            stock_price_next_day = stock_price_coll.find_one({"date": end})
            while stock_price_next_day is None and end <= last_date:
                end = increase_day_one(end)
                stock_price_next_day = stock_price_coll.find_one({"date": end}

            if stock_price_next_day is None:
                logging.debug("%s:There is no end date for start date %s",
                              company,
                              start)
                start = increase_day_one(start)
                continue

            # TODO checkpoint

            # get all tweets between two trading days
            trading_start = datetime.datetime(start.year, start.month, start.day, 14, 30)
            trading_start_next_day = trading_start + datetime.timedelta(days=1)
            twitter_tweets = twitter_coll.find({ "date": { "$gte": trading_start, "$lt": trading_start_next_day } })
            twitter_tweets_text = [(clean_text(tweet["text"]), tweet["date"]) for tweet in twitter_tweets]

            stocktwits_tweets = twitter_coll.find({ "date": { "$gte": trading_start, "$lt": trading_start_next_day } })
            stocktwits_tweets_text = [(clean_text(stocktwits_get_text(tweet)), tweet["date"]) for tweet in stocktwits_tweets]

            if not twitter_tweets_text and not stocktwits_tweets_text:
                start = start + datetime.timedelta(days=1)
                continue

            # get sentiment
            twitter_tweets_sentiment = [get_sentiment(tweet[0]) for tweet in twitter_tweets_text]
            stocktwits_tweets_sentiment = [get_sentiment(tweet[0]) for tweet in stocktwits_tweets_text]

            # create list with tuples of text and sentiment
            tweets = [{"text": text[0], "date": text[1], "sentiment": sentiment} for text, sentiment in zip(twitter_tweets_text, twitter_tweets_sentiment)]
            tweets.extend([{"text": text[0], "date": text[1], "sentiment": sentiment} for text, sentiment in zip(stocktwits_tweets_text, stocktwits_tweets_sentiment)])
            tweets.sort(key=lambda x: x["date"])
            
            # create sample
            sample = dict()
            sample["start"] = trading_start
            sample["end"] = trading_start_next_day
            sample["tweets"] = tweets
            sample["price_diff"] = get_relatvie_price_difference(stock_price_day, stock_price_next_day)

            learning_company_coll.update_one({"start": trading_start}, {"$set": sample}, upsert=True)

            start = end


def main():
    if sys.platform == "linux":
        base_path = os.path.join(Path.home(), "stock/stock-prediction")
    else:
        path = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        base_path = os.path.join(Path.home(), path)

    path = "preprocessing/logs/create_training_data_set.log"
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

    create_training_samples(sp500, first_date, last_date)


if __name__ == '__main__':
    main()
