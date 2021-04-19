import datetime
import json
import logging
import os
import pandas as pd
import sys
from pathlib import Path
from pymongo import MongoClient


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def check(sp500: list, database_name: str, output_path: str):
    client = MongoClient()
    database = client[database_name]

    for company in sp500:
        collection = database[company]

        days = []
        tweet_count = []

        start_day = datetime.datetime(2019, 4, 1)
        end_day = datetime.datetime.now()
        current_day = start_day

        while current_day < end_day:
            logging.debug("Check %s on %s", company, current_day)
            next_day = current_day + datetime.timedelta(days=1)
            num_tweets = collection.count_documents(
                    {"date": {"$gte": current_day,
                              "$lt": next_day}})
            days.append(current_day)
            tweet_count.append(num_tweets)

            current_day = current_day + datetime.timedelta(days=1)

        data_frame = pd.DataFrame({"day": days, "tweet_count": tweet_count})
        file_name = "tweet_count_{}_{}.csv".format(database_name, company)
        data_frame.to_csv(os.path.join(output_path, file_name))


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        path = os.path.join(Path.home(),
                            "Studies/Master/10SS19/StockPrediction")
        path = os.path.join(path, "stock-prediction")
    stats_path = os.path.join(path, "stats")
    crawling_path = os.path.join(path, "crawling")
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    log_path = os.path.join(stats_path, "log/count_tweets.log")
    output_path = os.path.join(stats_path, "output")

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s")
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    databases = ["twitterdb", "stocktwitsdb"]
    for database in databases:
        check(sp500, database, output_path)


if __name__ == "__main__":
    main()
