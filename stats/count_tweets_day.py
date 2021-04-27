import argparse
import datetime
import json
import logging
import os
import pandas as pd
import sys
import threading
from pathlib import Path
from pymongo import MongoClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.threads import divide_in_chunks
from util.read_sp500 import read_sp500


def start_with_threads(task, sp500: list, database, output_path: str):
    num_threads = 12
    sp500_chunks = list(divide_in_chunks(sp500, num_threads))

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=task,
                                  args=(sp500_chunks[i],
                                        database,
                                        output_path))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


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
        path = os.path.join(Path.home(), "stock/stock-prediction")
    else:
        path = os.path.join(Path.home(),
                            "Studies/Master/10SS19/StockPrediction")
        path = os.path.join(path, "stock-prediction")
    stats_path = os.path.join(path, "stats")
    crawling_path = os.path.join(path, "crawling")
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    log_path = os.path.join(stats_path, "log/count_tweets_day.log")
    output_path = os.path.join(stats_path, "output")

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s")
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    databases = ["stocktwitsdb", "twitterdb"]
    for database in databases:
        if args.threading:
            start_with_threads(check, sp500, database, output_path)
        else:
            check(sp500, database, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count tweets")
    parser.add_argument("--threading", action="store_true",
                        help="Enable threading")
    args = parser.parse_args()

    main()
