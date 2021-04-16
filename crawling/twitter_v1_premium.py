import datetime
import json
import logging
import os
import random
import re
import requests
import time
from pathlib import Path
from pymongo import MongoClient
from requests_oauthlib import OAuth1
from read_sp500 import read_sp500


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
            url = "https://api.twitter.com/1.1/tweets/search/30day/dev.json"
            from_date = datetime.date.today()
            from_date = from_date - datetime.timedelta(days=2)
            from_date_str = from_date.strftime("%Y%m%d") + "0000"
            max_results = 100

            query_dollar = {"query": "$" + company,
                            "fromDate": from_date_str,
                            "maxResults": max_results}
            query_hashtag = {"query": "#" + company,
                             "fromDate": from_date_str,
                             "maxResults": max_results}
            queries = [json.dumps(query_dollar), json.dumps(query_hashtag)]

            for query in queries:
                succeeded = False
                while not succeeded:
                    try:
                        result = requests.post(url, query, auth=auth)
                        result_json = result.json()
                        if "errors" in result_json:
                            logging.info("sleeping for 15 min")
                            time.sleep(900)
                        else:
                            succeeded = True
                    except Exception as exception:
                        logging.debug(str(exception))

                # debugging
                print(result_json)
                return

                tweets = result_json["statuses"]
                logging.info("%d results for %s", len(tweets), company)
                collection = database[company]
                for tweet in tweets:
                    parse_str = "%a %b %d %H:%M:%S %z %Y"
                    date = datetime.datetime.strptime(tweet["created_at"],
                                                      parse_str)
                    tweet["date"] = date

                    db_query = {
                        "text": tweet["text"],
                        "date": tweet["date"]
                        }
                    collection.update_one(db_query,
                                          {"$set": tweet},
                                          upsert=True)


def main():
    crawling_path = os.path.join(Path.home(), "stock-prediction/crawling")
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    log_path = os.path.join(crawling_path, "log/twitter_v1.log")
    access_token_path = os.path.join(crawling_path,
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


if __name__ == '__main__':
    main()
