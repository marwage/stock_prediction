import json
import logging
from datetime import datetime
import os
from pathlib import Path
from pymongo import MongoClient
import re
import sys


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def add_dates(do_twitter_db: bool, do_stocktwits_db: bool):
    client = MongoClient()
    learning_db = client["learning"]
    twitter_db = client["twitterdb"]
    stocktwits_db = client["stocktwitsdb"]

    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        path = os.path.join(Path.home(), "Studies/Master/10SS19/StockPrediction/stock-prediction")
    sp500_path = os.path.join(path, "crawling/data/sp500.json")
    sp500 = read_sp500(sp500_path)

    if do_twitter_db:
        for company in sp500:
            collection = twitter_db[company]
            tweets = collection.find()
            for post in tweets:
                if "date" not in post:
                    d = datetime.strptime(post["created_at"], "%a %b %d %H:%M:%S %z %Y")
                    collection.update_one({"_id": post["_id"]}, {"$set": {"date": d}})

    if do_stocktwits_db:
        for company in sp500:
            collection = stocktwits_db[company]
            tweets = collection.find()
            for post in tweets:
                if "date" not in post:
                    d = datetime.fromisoformat(re.sub("Z", "", post["created_at"]))
                    collection.update_one({"_id": post["_id"]}, {"$set": {"date": d}})


def main():
    do_twitter_db = True
    do_stocktwits_db = False
    add_dates(do_twitter_db, do_stocktwits_db)


if __name__ == '__main__':
    main()

