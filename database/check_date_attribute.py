import argparse
import datetime
import json
import logging
import os
import re
import sys
from pymongo import MongoClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.threads import start_with_threads
from util.read_sp500 import read_sp500


def check_date(sp500: list):
    client = MongoClient()
    database_names = ["stocktwitsdb", "twitterdb"]
    num_wrong_dates = 0

    for database_name in database_names:
        for company in sp500:
            logging.debug("%s:%s:Check", database_name, company)
            num_wrong_dates_company = 0
            database = client[database_name]
            collection = database[company]
            cursor = collection.find({}, batch_size=64)
            for tweet in cursor:
                if "date" in tweet:
                    date_attribute = tweet["date"]
                    if isinstance(date_attribute, datetime.datetime):
                        logging.debug("Date is fine")
                        continue
                    if isinstance(date_attribute, str):
                        logging.info("%s:%s:Date is String",
                                     database_name,
                                     company)
                        num_wrong_dates_company = num_wrong_dates_company + 1
                    else:
                        logging.error("Date is neither datetime nor str")
                else:
                    logging.info("%s:%s:Date does not exist",
                                 database_name,
                                 company)
                    num_wrong_dates_company = num_wrong_dates_company + 1
            logging.info("%s:%s:Wrong dates: %d",
                         database_name,
                         company,
                         num_wrong_dates_company)
            num_wrong_dates = num_wrong_dates + num_wrong_dates_company

    logging.info("Wrong dates %d", num_wrong_dates)
    print("{} wrong dates".format(num_wrong_dates))


def main():
    sp500_path = os.path.join("../crawling", "data/sp500.json")
    log_path = os.path.join(".", "log/check_date_attribute.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

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
