import json
import logging
from datetime import datetime
import os
from pathlib import Path
from pymongo import MongoClient


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def create_training_samples():
    client = MongoClient()
    learning_db = client["learning"]
    twitter_db = client["twitterdb"]
    stocktwits_db = client["stocktwitsdb"]

    sp500_path = os.path.join(Path.home(), "stock-prediction/crawling/data/sp500.json")
    sp500 = read_sp500(sp500_path)

    for company in sp500:
        collection = twitter_db[company]
        tweets = collection.find()
        for post in tweets:
            d = datetime.strptime(post["created_at"], "%a %b %d %H:%M:%S %z %Y").isoformat()
            collection.update_one({"_id": post["_id"]}, {"$set": {"date": d}})

    for company in sp500:
        collection = stocktwits_db[company]
        tweets = collection.find()
        for post in tweets:
            print(post)
            return


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
