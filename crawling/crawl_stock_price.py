import json
import logging
import os
import random
import re
import requests
import sys
import time
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient
from read_sp500 import read_sp500


def get_apikey(path):
    with open(path, "r") as json_file:
        apikey_json = json.load(json_file)
    return apikey_json["apikey"]


def query_stock_price(apikey, sp500):
    client = MongoClient()
    stockprice_db = client["stockpricedb"]
    time_zone_db = client["timezonedb"]

    exclude_already_crawled = False
    if exclude_already_crawled:
        collection_names = time_zone_db.list_collection_names()

    for company in sp500:
        if exclude_already_crawled and company in collection_names:
            continue

        sucessful = False
        while not sucessful:
            request_url = "https://www.alphavantage.co/query" \
                        + "?function=TIME_SERIES_DAILY&symbol=" \
                        + re.sub(r"\.", "-", company) \
                        + "&outputsize=full&apikey=" + apikey
            result = requests.get(request_url)
            if result.status_code == 200:
                json_result = result.json()
                if "Time Series (Daily)" in json_result:
                    sucessful = True
                elif "Note" in json_result:
                    logging.debug(json_result["Note"])
                    time.sleep(90)
                elif "Information" in json_result:
                    logging.debug(json_result["Information"])
                    time.sleep(90)
                else:
                    logging.error("URL is not working: %s, JSON: %s",
                                  request_url,
                                  json.dumps(json_result))
            else:
                logging.error("Request failed with error code: %s",
                              str(result.status_code))

        collection = time_zone_db[company]
        time_zone = json_result["Meta Data"]["5. Time Zone"]
        collection.update_one({},
                              {"$set": {"time_zone": time_zone}},
                              upsert=True)

        collection = stockprice_db[company]
        for key, value in json_result["Time Series (Daily)"].items():
            date = datetime.strptime(key, "%Y-%m-%d")
            if date > datetime(2019, 6, 1):
                day_properties = dict()
                day_properties["date"] = date
                day_properties["open"] = float(value["1. open"])
                day_properties["high"] = float(value["2. high"])
                day_properties["low"] = float(value["3. low"])
                day_properties["close"] = float(value["4. close"])
                day_properties["volume"] = int(value["5. volume"])

                collection.update_one({"date": date},
                                      {"$set": day_properties},
                                      upsert=True)


def main():
    if sys.platform == "linux":
        crawling_path = os.path.join(Path.home(), "stock-prediction/crawling")
    else:
        directory = "Studies/Master/10SS19/StockPrediction/" \
                  + "stock-prediction/crawling"
        crawling_path = os.path.join(Path.home(), directory)
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    apikey_path = os.path.join(crawling_path,
                               "access_token/alpha_vantage_apikey.json")
    log_path = os.path.join(crawling_path, "log/crawl_stock_price.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    apikey = get_apikey(apikey_path)
    sp500 = read_sp500(sp500_path)
    random.shuffle(sp500)
    query_stock_price(apikey, sp500)


if __name__ == '__main__':
    main()
