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

def get_sentiment(text):
    text_blob = TextBlob(text)
    return text_blob.sentiment.polarity

def get_relative_price_difference(day, next_day):
    stock_price_day = day["open"]
    stock_price_next_day = next_day["open"]
    return (stock_price_next_day - stock_price_day) / stock_price_day


def create_training_samples(mongo_client: MongoClient,
                            sp500: list,
                            first_date: datetime,
                            last_date: datetime,
                            dataset_db_name: str):
    dataset_db = mongo_client[dataset_db_name]
    twitter_db = mongo_client["twitterdb"]
    stockprice_db = mongo_client["stockpricedb"]

    for company in sp500:
        logging.info("Create training samples for %s", company)

        twitter_coll = twitter_db[company]
        dataset_coll = dataset_db[company]
        stock_price_coll = stockprice_db[company]

        # for each day
        start = first_date
        while start <= last_date:
            stock_price_day = stock_price_coll.find_one({"date": start})

            if stock_price_day is None:
                start = start + timedelta(days=1)
                continue

            # get next trading day
            end = start + timedelta(days=1)
            stock_price_next_day = stock_price_coll.find_one({"date": end})
            while stock_price_next_day is None and end <= last_date:
                end = end + timedelta(days=1)
                stock_price_next_day = stock_price_coll.find_one({"date": end})

            if stock_price_next_day is None:
                logging.debug("%s: There is no end date for start date %s",
                              company,
                              start)

                start = start + timedelta(days=1)
                continue

            # get all tweets between two trading days
            trading_start = datetime(start.year, start.month, start.day, 14, 30)
            trading_start_next_day = trading_start + timedelta(days=1)
            twitter_tweets = twitter_coll.find({"date": {"$gte": trading_start,
                                                         "$lt": trading_start_next_day}})

            tweets = []
            for tweet in twitter_tweets:
                # filter English tweets only
                if tweet["lang"] == "en":
                    try:
                        tweet_features = dict()
                        tweet_features["text"] = clean_text(tweet["text"])
                        tweet_features["sentiment"] = get_sentiment(tweet_features["text"])
                        tweet_features["date"] = tweet["date"]
                        tweet_features["followers"] = tweet["user"]["followers_count"]
                        if "retweeted_count" in tweet:
                            tweet_features["retweets"] = tweet["retweeted_count"]
                        else:
                            tweet_features["retweets"] = 0

                        tweets.append(tweet_features)
                    except:
                        logging.debug("%s: Tweet does not have attribute: %s",
                                      company,
                                      tweet)

            # filter more than 240 tweets
            tweets_threshold = 240
            num_tweets = len(tweets)
            if num_tweets < tweets_threshold:
                start = start + timedelta(days=1)
                logging.debug("%s: There are %s < %s tweets",
                              company,
                              num_tweets,
                              tweets_threshold)
                continue

            # create features list sorted by date
            tweets.sort(key=lambda x: x["date"])
            # extract features
            tweets_features = [[tweet["sentiment"], tweet["followers"], tweet["retweets"]] for tweet in tweets]

            # create sample
            sample = dict()
            sample["start"] = trading_start
            sample["end"] = trading_start_next_day
            sample["tweets"] = tweets_features
            sample["price_diff"] = get_relative_price_difference(stock_price_day,
                                                                 stock_price_next_day)

            dataset_coll.update_one({"start": trading_start},
                                    {"$set": sample},
                                    upsert=True)

            start = end


def main():
    sp500_path = os.path.join("../crawling", "data/sp500.json")
    log_path = os.path.join(".", "log/create_training_samples_twitter.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    
    sp500 = read_sp500(sp500_path)

    first_date = datetime(2019, 6, 1)
    last_date = datetime(2021, 3, 12)

    mongo_client = MongoClient()

    samples_db = "twitter_three"
    create_training_samples(mongo_client,
                            sp500,
                            first_date,
                            last_date,
                            samples_db)


if __name__ == '__main__':
    main()
