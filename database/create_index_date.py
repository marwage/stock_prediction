import logging
import os
import sys
from pathlib import Path
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
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock/stock-prediction")
    else:
        directory = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        path = os.path.join(Path.home(), directory)
    sp500_path = os.path.join(path, "crawling/data/sp500.json")
    log_path = os.path.join(path, "database/log/create_index_date.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    sp500 = read_sp500(sp500_path)
    create_index_date(sp500)


if __name__ == "__main__":
    main()
