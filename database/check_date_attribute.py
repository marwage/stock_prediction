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


def check_date(sp500: list):
    client = MongoClient()
#      database_names = ["stocktwitsdb", "twitterdb"]
    database_names = ["stocktwitsdb"]
    num_wrong_dates = 0

    for database_name in database_names:
        for company in sp500:
            logging.info("Check %s %s", database_name, company)
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
                        num_wrong_dates = num_wrong_dates + 1
                    else:
                        logging.error("Date is neither datetime nor str")
                else:
                    logging.info("%s:%s:Date does not exist",
                                 database_name,
                                 company)
                    num_wrong_dates = num_wrong_dates + 1

    logging.info("%d wrong dates", num_wrong_dates)
    print("{} wrong dates".format(num_wrong_dates))


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock/stock-prediction")
    else:
        directory = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        path = os.path.join(Path.home(), directory)
    sp500_path = os.path.join(path, "crawling/data/sp500.json")
    log_path = os.path.join(path, "database/log/check_date.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    sp500 = read_sp500(sp500_path)

    if args.threading:
        start_with_threads(check_date, sp500)
    else:
        check_date(sp500)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix date attribute")
    parser.add_argument("--threading", action="store_true",
                        help="Enable threading")
    args = parser.parse_args()

    main()
