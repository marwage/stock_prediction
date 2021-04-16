import json
import time
import random
import os
import re
import sys
from pathlib import Path
import logging
import requests
from pymongo import MongoClient
from read_sp500 import read_sp500


def get_apikey(path):
    with open(path, "r") as json_file:
        apikey_json = json.load(json_file)

    return apikey_json["apikey"]


def query_company_info(apikey, sp500):
    client = MongoClient()
    info_db = client["companyinfodb"]
    collection_names = info_db.list_collection_names()

    for company in sp500:
        logging.debug("Crawling for company %s", company)

        if company in collection_names:
            continue

        # UTX not working
        if company == "UTX":
            continue

        sucessful = False
        while not sucessful:
            # https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo
            request_url = "https://www.alphavantage.co/query" \
                        + "?function=OVERVIEW&symbol=" \
                        + re.sub(r"\.", "-", company) + "&apikey=" + apikey
            result = requests.get(request_url)
            if result.status_code == 200:
                json_result = result.json()
                sleep_time = 70
                if "Symbol" in json_result:
                    sucessful = True
                elif "Note" in json_result:
                    logging.debug(json_result["Note"])
                    time.sleep(sleep_time)
                elif "Information" in json_result:
                    logging.debug(json_result["Information"])
                    time.sleep(sleep_time)
                else:
                    logging.error("URL is not working: %s, JSON: %s",
                                  request_url,
                                  json.dumps(json_result))
                    return  # most likely symbol not working
            else:
                logging.error("Request failed with error code: %s",
                              str(result.status_code))

        collection = info_db[company]
        collection.update_one({"Symbol": company},
                              {"$set": json_result},
                              upsert=True)


def main():
    if sys.platform == "linux":
        crawling_path = os.path.join(Path.home(), "stock-prediction/crawling")
    else:
        directory = "Studies/Master/10SS19/StockPrediction" \
                  + "/stock-prediction/crawling"
        crawling_path = os.path.join(Path.home(), directory)
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    apikey_path = os.path.join(crawling_path,
                               "access_token/alpha_vantage_apikey.json")
    log_path = os.path.join(crawling_path, "log/company_info.log")

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
