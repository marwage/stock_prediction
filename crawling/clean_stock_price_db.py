import datetime
import logging
import os
import pandas as pd
import sys
from pathlib import Path
from pymongo import MongoClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def clean(sp500: list):
    client = MongoClient()
    stockprice_db = client["stockpricedb"]

    for company in sp500:
        logging.info("Clean %s", company)
        collection = stockprice_db[company]
        cursor = collection.find()
        for day in cursor:
            if "date" not in day:
                delete_result = collection.delete_one({"_id": day["_id"]})
                logging.debug("Delete acknowledged: %s",
                              delete_result.acknowledged)

def main():
    if sys.platform == "linux":
        crawling_path = os.path.join(Path.home(), "stock-prediction/crawling")
    else:
        directory = "Studies/Master/10SS19/StockPrediction/" \
                  + "stock-prediction/crawling"
        crawling_path = os.path.join(Path.home(), directory)
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    log_path = os.path.join(crawling_path, "log/clean_stock_price_db.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    sp500 = read_sp500(sp500_path)
    clean(sp500)


if __name__ == '__main__':
    main()
