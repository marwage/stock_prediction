import json
import logging
import os
import random
import re
import requests
import sys
import time
from datetime import timedelta, datetime
from pathlib import Path
from pymongo import MongoClient
from requests_oauthlib import OAuth1
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def read_access_token(access_token_path):
    with open(access_token_path, "r") as access_token_file:
        access_token = json.load(access_token_file)

    return access_token


def crawl_twitter(sp500, access_token):
    client = MongoClient()
    database = client.twitterdb

    auth = OAuth1(access_token["consumer_key"],
                  access_token["consumer_secret"],
                  access_token["access_token_key"],
                  access_token["access_token_secret"])

    while True:
        for company in sp500:
            q_dollar = "https://api.twitter.com/1.1/search/tweets.json?q=" \
                + "%24" + company \
                + "&result_type=recent&count=100"
            q_hashtag = "https://api.twitter.com/1.1/search/tweets.json?q=" \
                + "%23" + company + "&result_type=recent&count=100"
            queries = [q_dollar, q_hashtag]

            for query in queries:
                succeeded = False
                while not succeeded:
                    try:
                        result = requests.get(query, auth=auth)
                        result_json = result.json()
                        if "errors" in result_json:
                            logging.info("sleeping for 15 min")
                            time.sleep(900)
                        else:
                            succeeded = True
                    except Exception as exception:
                        logging.debug(str(exception))

                tweets = result_json["statuses"]
                logging.info("%d results for %s", len(tweets), company)
                collection = database[company]
                for tweet in tweets:
                    date = datetime.strptime(tweet["created_at"],
                                             "%a %b %d %H:%M:%S %z %Y")
                    tweet["date"] = date

                    db_query = {
                        "text": tweet["text"],
                        "date": tweet["date"]
                        }
                    collection.update_one(db_query,
                                          {"$set": tweet},
                                          upsert=True)


def main():
    sp500_path = os.path.join(".", "data/sp500.json")
    log_path = os.path.join(".", "log/twitter_v1.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    access_token_path = os.path.join(".",
                                     "access_token/twitter_access_token.json")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    random.shuffle(sp500)
    access_token = read_access_token(access_token_path)
    crawl_twitter(sp500, access_token)


if __name__ == "__main__":
    main()
