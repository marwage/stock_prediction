import logging
import os
import sys
from pymongo import MongoClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def create_index_date(sp500: list):
    client = MongoClient()
    database_names = ["stocktwitsdb", "twitterdb", "stockpricedb"]

    for database_name in database_names:
        database = client[database_name]
        for company in sp500:
            collection = database[company]
            logging.info("%s:%s:Create date index", database_name, company)
            collection.create_index("date")


def main():
    sp500_path = os.path.join("../crawling", "data/sp500.json")
    log_path = os.path.join(".", "log/create_index_date.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    sp500 = read_sp500(sp500_path)
    create_index_date(sp500)


if __name__ == "__main__":
    main()
