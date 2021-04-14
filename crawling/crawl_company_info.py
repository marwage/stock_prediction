import requests
import json
from pymongo import MongoClient
from datetime import datetime
import time
import random
import logging
from read_sp500 import read_sp500
import os
from pathlib import Path
import sys
import re


def get_apikey(path):
    with open(path, "r") as json_file:
        apikey_json = json.load(json_file)

    return apikey_json["apikey"]


def query_company_info(apikey, sp500):
    client = MongoClient()
    info_db = client["companyinfodb"]

    for company in sp500:
        sucessful = False
        while not sucessful:
            # https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo
            request_url = "https://www.alphavantage.co/query" \
                        + "?function=OVERVIEW&symbol=" \
                        + re.sub(r"\.", "-", company) + "&apikey=" + apikey
            result = requests.get(request_url)
            if result.status_code == 200:
                json_result = result.json()
                if "Symbol" in json_result:
                    sucessful = True
                elif "Note" in json_result:
                    logging.debug(json_result["Note"])
                    time.sleep(90)
                elif "Information" in json_result:
                    logging.debug(json_result["Information"])
                    time.sleep(90)
                else:
                    logging.error("URL is not working: %s, JSON: %s", request_url, json.dumps(json_result))
            else:
                logging.error("Request failed with error code: %s", str(result.status_code))

        collection = info_db[company]
        collection.update_one({"Symbol": company}, {"$set": json_result }, upsert=True)


def main():
    if sys.platform == "linux":
        crawling_path = os.path.join(Path.home(), "stock-prediction/crawling")
    else:
        crawling_path = os.path.join(Path.home(), "Studies/Master/10SS19/StockPrediction/stock-prediction/crawling")
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    apikey_path = os.path.join(crawling_path, "access_token/alpha_vantage_apikey.json")
    log_path = os.path.join(crawling_path, "log/crawl_company_info.log")

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
    query_company_info(apikey, sp500)


if __name__ == '__main__':
    main()
