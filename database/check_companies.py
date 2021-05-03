import logging
import os
import sys
from pymongo import MongoClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def check_companies(sp500: list):
    client = MongoClient()
    database_names = ["stocktwitsdb", "twitterdb"]

    for database_name in database_names:
        database = client[database_name]
        collection_names = database.list_collection_names()
        names_set = set(collection_names)
        sp500_set = set(sp500)
        only_in_sp500 = sp500_set.difference(names_set)
        logging.info("%s: Only in S&P500  %s", database_name, only_in_sp500)


def main():
    sp500_path = os.path.join("../crawling", "data/sp500.json")
    log_path = os.path.join(".", "log/check_companies.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    sp500 = read_sp500(sp500_path)
    check_companies(sp500)


if __name__ == "__main__":
    main()
