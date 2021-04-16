import json
import logging
import os
import re
import requests
import sys
import time
from datetime import timedelta, datetime
from pathlib import Path
from pymongo import MongoClient
from read_sp500 import read_sp500
from requests_oauthlib import OAuth1


def read_access_token(access_token_path):
    with open(access_token_path, "r") as access_token_file:
        access_token = json.load(access_token_file)

    return access_token


def crawl_twitter(sp500, access_token):
    client = MongoClient()
    database = client["twitterv2"]

    auth = OAuth1(access_token["consumer_key"],
                  access_token["consumer_secret"],
                  access_token["access_token_key"],
                  access_token["access_token_secret"])

    while True:
        for company in sp500:
            query = "https://api.twitter.com/2/tweets/search/recent?query=" \
                  + "%23" + company \
                  + "&max_results=100" \
                  + "&tweet.fields=created_at,public_metrics,lang"

            succeeded = False
            while not succeeded:
                try:
                    result = requests.get(query, auth=auth)
                    result_json = result.json()

                    if "errors" in result_json:
                        logging.debug("sleeping for 15 min")
                        time.sleep(900)
                    else:
                        succeeded = True
                except Exception as e:
                    logging.debug(str(e))

            if "data" in result_json:
                tweets = result_json["data"]

                logging.info("%d results for %s", len(tweets), company)

                collection = database[company]
                for tweet in tweets:
                    created_at = re.sub("Z", "", tweet["created_at"])
                    date = datetime.fromisoformat(created_at)
                    tweet["date"] = date

                    db_query = {
                        "text": tweet["text"],
                        "date": date
                        }
                    collection.update_one(db_query,
                                          {"$set": tweet},
                                          upsert=True)


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        directory = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        path = os.path.join(Path.home(), directory)
    crawling_path = os.path.join(path, "crawling")
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    log_path = os.path.join(crawling_path, "log/crawl_twitter_v2.log")
    access_token_path = os.path.join(crawling_path,
                                     "access_token/twitter_access_token.json")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    access_token = read_access_token(access_token_path)
    crawl_twitter(sp500, access_token)


if __name__ == '__main__':
    main()
