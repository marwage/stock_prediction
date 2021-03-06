import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from textblob import TextBlob


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)
    return sp500_json["sp500"]

def clean_text(text):
    cleaned = re.sub(r"\n+", " ", text)
    cleaned = re.sub(r" {2,}", " ", cleaned)
    cleaned = re.sub(r"((http|https)://)(www.)?[a-zA-Z0-9@:%._\+~#?&//=]{1,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%._\+~#?&//=]*)",
                     "", cleaned)
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


def create_training_samples(mongo_client: MongoClient, sp500: list, first_date: datetime, last_date: datetime):
    learning_db = mongo_client["learning"]
    twitter_db = mongo_client["twitterdb"]
    stocktwits_db = mongo_client["stocktwitsdb"]
    stockprice_db = mongo_client["stockpricedb"]

    for company in sp500:
        logging.info("Create training samples for %s", company)

        twitter_company_coll = twitter_db[company]
        stocktwits_company_coll = stocktwits_db[company]
        learning_company_coll = learning_db[company]
        stock_price_company_coll = stockprice_db[company]

        # for each day
        start = first_date
        while start <= last_date:
            stock_price_day = stock_price_company_coll.find_one({"date": start})

            if stock_price_day is None:
                start = start + timedelta(days=1)
                continue

            # get next trading day
            end = start + timedelta(days=1)
            stock_price_next_day = stock_price_company_coll.find_one({"date": end})
            while stock_price_next_day is None and end <= last_date:
                end = end + timedelta(days=1)
                stock_price_next_day = stock_price_company_coll.find_one({"date": end})

            if stock_price_next_day is None:
                logging.debug("%s: There is no end date for start date %s", company, start)

                start = start + timedelta(days=1)
                continue

            # get all tweets between two trading days
            trading_start = datetime(start.year, start.month, start.day, 14, 30)
            trading_start_next_day = trading_start + timedelta(days=1)
            twitter_tweets = twitter_company_coll.find({ "date": { "$gte": trading_start, "$lt": trading_start_next_day } })
            twitter_tweets_text = [(clean_text(tweet["text"]), tweet["date"]) for tweet in twitter_tweets]

            stocktwits_tweets = stocktwits_company_coll.find({ "date": { "$gte": trading_start, "$lt": trading_start_next_day } })
            stocktwits_tweets_text = [(clean_text(stocktwits_get_text(tweet)), tweet["date"]) for tweet in stocktwits_tweets]

            if not twitter_tweets_text and not stocktwits_tweets_text:
                start = start + timedelta(days=1)
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
            sample["price_diff"] = get_relative_price_difference(stock_price_day, stock_price_next_day)

            learning_company_coll.update_one({"start": trading_start}, {"$set": sample}, upsert=True)

            start = end


def main():
    sp500_path = os.path.join("../crawling", "data/sp500.json")
    log_path = os.path.join(".", "log/create_training_samples.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    sp500 = read_sp500(sp500_path)

    first_date = datetime(2019, 6, 1)
    last_date = datetime(2021, 1, 15)

    mongo_client = MongoClient()

    create_training_samples(mongo_client, sp500, first_date, last_date)


if __name__ == '__main__':
    main()
