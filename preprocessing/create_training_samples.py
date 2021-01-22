import json
import logging
from datetime import datetime, timedelta
import os
from pathlib import Path
from pymongo import MongoClient
import re


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


def create_training_samples():
    client = MongoClient()
    learning_db = client["learning"]
    twitter_db = client["twitterdb"]
    stocktwits_db = client["stocktwitsdb"]

    sp500_path = os.path.join(Path.home(),
            "Studies/Master/10SS19/StockPrediction/stock-prediction/crawling/data/sp500.json")
    sp500 = read_sp500(sp500_path)

    start = datetime(2019, 6, 1)
    end = datetime(2021, 1, 15)

    for company in sp500:
        twitter_company_coll = twitter_db[company]
        stocktwits_company_coll = stocktwits_db[company]
        learning_company_coll = learning_db[company]

        print(company)

        # for each day
        timestamp_a = start
        while timestamp_a <= end:
            timestamp_b = timestamp_a + timedelta(days=1)

            twitter_tweets = twitter_company_coll.find({ "date": { "$gte": timestamp_a, "$lt": timestamp_b } })
            stocktwits_tweets = twitter_company_coll.find({ "date": { "$gte": timestamp_a, "$lt": timestamp_b } })

            day = dict()
            day["day"] = timestamp_a
            twitter_tweets_text = [clean_text(tweet["text"]) for tweet in twitter_tweets]
            stocktwits_tweets_text = [clean_text(stocktwits_get_text(tweet)) for tweet in stocktwits_tweets]
            twitter_tweets_sentiment = [0 for tweet in twitter_tweets_text]
            stocktwits_tweets_sentiment = [0 for tweet in stocktwits_tweets_text]

            tweets = [{"text": text, "sentiment": sentiment} for text, sentiment in zip(twitter_tweets_text, twitter_tweets_sentiment)]
            tweets.extend([{"text": text, "sentiment": sentiment} for text, sentiment in zip(stocktwits_tweets_text, stocktwits_tweets_sentiment)])
            day["tweets"] = tweets
            day["price_diff"] = 0

            if day["tweets"]:
                learning_company_coll.update_one({"day": timestamp_a}, {"$set": day}, upsert=True)

            timestamp_a = timestamp_b


def main():
    create_training_samples()


if __name__ == '__main__':
    main()
