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


def create_training_samples():
    client = MongoClient()
    learning_db = client["learning"]
    twitter_db = client["twitterdb"]
    stocktwits_db = client["stocktwitsdb"]

    sp500_path = os.path.join(Path.home(), "stock-prediction/crawling/data/sp500.json")
    sp500 = read_sp500(sp500_path)

    for company in sp500:
        if company == "AAPL":
            collection = twitter_db[company]

            tweets = collection.find()
            for i, post in enumerate(tweets):
                print(clean_text(post["text"]))
                if i > 20:
                    return

    start = datetime(2019, 6, 1)
    end = datetime(2021, 1, 15)

    timestamp = start
    # for each day
    while timestamp <= end:
        timestamp += timedelta(year=1)


def main():
    # log_path = ""
    # logging.basicConfig(
    #     filename=log_path,
    #     level=logging.DEBUG,
    #     format="%(asctime)s:%(levelname)s:%(message)s"
    #     )

    create_training_samples()


if __name__ == '__main__':
    main()
