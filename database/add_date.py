import datetime
import json
import os
import re
from pymongo import MongoClient


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def add_dates(data_base_name: str, sp500: list):
    client = MongoClient()
    twitter_db = client["twitterdb"]
    stocktwits_db = client["stocktwitsdb"]


    if data_base_name == "twitterdb":
        for company in sp500:
            collection = twitter_db[company]
            tweets = collection.find()
            for post in tweets:
                if "date" not in post:
                    parse_pattern = "%a %b %d %H:%M:%S %z %Y"
                    date = datetime.datetime.strptime(post["created_at"],
                                                      parse_pattern)
                    collection.update_one({"_id": post["_id"]},
                                          {"$set": {"date": date}})
    elif data_base_name == "stocktwitsdb":
        for company in sp500:
            collection = stocktwits_db[company]
            tweets = collection.find()
            for post in tweets:
                if "date" not in post:
                    date_str = re.sub("Z", "", post["created_at"])
                    date = datetime.datetime.fromisoformat(date_str)
                    collection.update_one({"_id": post["_id"]},
                                          {"$set": {"date": date}})


def main():
    sp500_path = os.path.join("../crawling", "data/sp500.json")

    sp500 = read_sp500(sp500_path)
    add_dates("twitterdb", sp500)
    add_dates("stocktwitsdb", sp500)


if __name__ == "__main__":
    main()
