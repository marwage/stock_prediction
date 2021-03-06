import datetime
import json
import logging
import os
import random
import re
import requests
import sys
import time
from pathlib import Path
from pymongo import MongoClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def get_apikey(path):
    with open(path, "r") as json_file:
        apikey_json = json.load(json_file)
    return apikey_json["apikey"]


def query_stock_price(apikey, sp500):
    start_date = datetime.datetime(2019, 4, 1)
    sleep_time = 95
    client = MongoClient()
    stockprice_db = client["stockpricedb"]
    time_zone_db = client["timezonedb"]

    for company in sp500:
        sucessful = False
        while not sucessful:
            url = "https://www.alphavantage.co/query"
            params = {"function": "TIME_SERIES_DAILY",
                      "symbol": re.sub(r"\.", "-", company),
                      "outputsize": "full",
                      "apikey": apikey}
            result = requests.get(url, params=params)
            if result.status_code == 200:
                json_result = result.json()
                if "Time Series (Daily)" in json_result:
                    sucessful = True
                elif "Note" in json_result:
                    logging.debug(json_result["Note"])
                    time.sleep(sleep_time)
                elif "Information" in json_result:
                    logging.debug(json_result["Information"])
                    time.sleep(sleep_time)
                else:
                    logging.warning("URL is not working: %s %s, JSON: %s",
                                    url,
                                    json.dumps(params),
                                    json.dumps(json_result))
            else:
                logging.warning("Request failed with error code: %s",
                                str(result.status_code))

        collection = time_zone_db[company]
        time_zone = json_result["Meta Data"]["5. Time Zone"]
        collection.update_one({"time_zone": time_zone},
                              {"$set": {"time_zone": time_zone}},
                              upsert=True)

        collection = stockprice_db[company]
        for key, value in json_result["Time Series (Daily)"].items():
            date = datetime.datetime.strptime(key, "%Y-%m-%d")
            if date > start_date:
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
    sp500_path = os.path.join(".", "data/sp500.json")
    apikey_path = os.path.join(".",
                               "access_token/alpha_vantage_apikey.json")
    log_path = os.path.join(".", "log/stock_price.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    apikey = get_apikey(apikey_path)
    sp500 = read_sp500(sp500_path)
    random.shuffle(sp500)
    query_stock_price(apikey, sp500)


if __name__ == "__main__":
    main()
