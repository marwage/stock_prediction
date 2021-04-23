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


def get_sentiment(text):
    text_blob = TextBlob(text)
    return text_blob.sentiment.polarity


def get_relative_price_difference(day, next_day):
    stock_price_day = day["open"]
    stock_price_next_day = next_day["open"]
    return (stock_price_next_day - stock_price_day) / stock_price_day


def increase_day_one(date: datetime.datetime):
    return date + datetime.timedelta(days=1)


def body(client: MongoClient,
         company: str,
         start_date: datetime.datetime,
         end_date: datetime.datetime,
         price_diff: float):
    trainingdataset_db = client["trainingdatasetdb"]
    twitter_db = client["twitterdb"]
    stocktwits_db = client["stocktwitsdb"]
    twitter_coll = twitter_db[company]
    stocktwits_coll = stocktwits_db[company]
    data_set_coll = trainingdataset_db["Ava"]

    trading_start = datetime.datetime(start_date.year,
                                      start_date.month,
                                      start_date.day,
                                      14, 30)
    trading_start_next_day = datetime.datetime(end_date.year,
                                               end_date.month,
                                               end_date.day,
                                               14, 30)

    # Twitter
    tweets = twitter_coll.find({"date": {"$gte": trading_start,
                                         "$lt": trading_start_next_day}})
    tweets_text = []
    for tweet in tweets:
        tweets_text.append((clean_text(tweet["text"]), tweet["date"]))
    tweets_sentiment = [get_sentiment(tweet[0]) for tweet in tweets_text]

    # Stocktwits
    # TODO
    ideas = stocktwits_coll.find({"date": {"$gte": trading_start,
                                           "$lt": trading_start_next_day}})
    ideas_text = []
    for idea in ideas:
        ideas_text.append((clean_text(idea["body"]), idea["date"]))
    ideas_sentiment = [get_sentiment(tweet[0]) for tweet in ideas_text]

    # Check if there are any tweets or ideas
    if not tweets_text and not ideas_text:
        start_date = start_date + datetime.timedelta(days=1)
        return False

    # Company Info
    # TODO

    # create data point
    day = dict()
    day["company"] = company
    day["start"] = trading_start
    day["end"] = trading_start_next_day
    day["price_diff"] = price_diff
    day["tweets"] = tweets

    data_set_coll.update_one({"start": trading_start, "company": company},
                             {"$set": day},
                             upsert=True)

    return True


def create_training_data_set(companies: list,
                             first_date: datetime.datetime,
                             last_date: datetime.datetime):
    client = MongoClient()
    stockprice_db = client["stockpricedb"]

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

            created_data_point = body(client,
                                      company,
                                      start_date,
                                      end_date,
                                      price_diff)
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

    create_training_data_set(sp500, first_date, last_date)


if __name__ == "__main__":
    main()
