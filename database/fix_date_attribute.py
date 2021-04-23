import argparse
import datetime
import json
import logging
import os
import re
import sys
from pathlib import Path
from pymongo import MongoClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.threads import start_with_threads
from util.read_sp500 import read_sp500


def update_tweet(tweet, collection, new_date: datetime.datetime):
    filtr = {"id": tweet["id"]}
    update = {"$set": {"date": new_date}}
    update_result = collection.update_one(filtr, update)
    logging.debug("update_one acknowledged: %s",
                  update_result.acknowledged)


def fix_tweet(tweet, collection):
    created_at = tweet["created_at"]
    try:
        date_str = re.sub("Z", "", created_at)
        new_date = datetime.datetime.fromisoformat(date_str)
        update_tweet(tweet, collection, new_date)
        return
    except ValueError:
        pass

    try:
        date_format = "%a %b %d %H:%M:%S %z %Y"
        new_date = datetime.datetime.strptime(created_at,
                                              date_format)
        update_tweet(tweet, collection, new_date)
        return
    except ValueError:
        pass

    logging.error("Both attempts to parse the date failed")


def fix_date(sp500: list):
    client = MongoClient()
    database_names = ["stocktwitsdb", "twitterdb"]

    for database_name in database_names:
        for company in sp500:
            logging.info("Fix %s %s", database_name, company)
            database = client[database_name]
            collection = database[company]
            cursor = collection.find({}, batch_size=64)
            for tweet in cursor:
                if "date" in tweet:
                    date_attribute = tweet["date"]
                    if isinstance(date_attribute, datetime.datetime):
                        logging.debug("Date is fine")
                        continue
                    elif isinstance(date_attribute, str):
                        logging.info("%s:%s:Date is String",
                                     database_name,
                                     company)
                        fix_tweet(tweet, collection)
                    else:
                        logging.error("Date is neither datetime nor str")
                else:
                    logging.info("%s:%s:Date does not exist",
                                 database_name,
                                 company)
                    fix_tweet(tweet, collection)


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock/stock-prediction")
    else:
        directory = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        path = os.path.join(Path.home(), directory)
    sp500_path = os.path.join(path, "crawling/data/sp500.json")
    log_path = os.path.join(path, "database/log/fix_date.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    sp500 = read_sp500(sp500_path)

    if args.threading:
        start_with_threads(fix_date, sp500)
    else:
        fix_date(sp500)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix date attribute")
    parser.add_argument("--threading", action="store_true",
                        help="Enable threading")
    args = parser.parse_args()

    main()
