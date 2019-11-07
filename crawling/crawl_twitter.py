import json
import time
import logging
import requests
from datetime import timedelta, datetime
from pymongo import MongoClient
from requests_oauthlib import OAuth1
from read_sp500 import read_sp500


def read_access_token(access_token_path):
    with open(access_token_path, "r") as access_token_file:
        access_token = json.load(access_token_file)

    return access_token


def crawl_twitter(sp500, access_token):
    client = MongoClient()
    db = client.twitterdb

    auth = OAuth1(access_token["consumer_key"], access_token["consumer_secret"],
        access_token["access_token_key"], access_token["access_token_secret"])

    while True:
        for company in sp500:
            query_dollar = "https://api.twitter.com/1.1/search/tweets.json?q=" + "%24"+ company + "&result_type=recent&count=100"
            query_hashtag = "https://api.twitter.com/1.1/search/tweets.json?q=" + "%23"+ company + "&result_type=recent&count=100"
            queries = [query_dollar, query_hashtag]
            
            for query in queries:
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
                    
                tweets = result_json["statuses"]
                logging.debug(str(len(tweets)) + " results for " + company)
                collection = db[company]
                for tweet in tweets:
                    db_query = {
                        "text": tweet["text"],
                        "created_at": tweet["created_at"]
                        }
                    write_result = collection.update(db_query, tweet, upsert=True)
                    

def main():
    crawling_path = "stock-prediction/crawling/"
    sp500_path = crawling_path + "data/sp500.json"
    log_path = crawling_path + "log/crawl_twitter.log"
    access_token_path = crawling_path + "access_token/twitter_access_token.json"

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    access_token = read_access_token(access_token_path)
    crawl_twitter(sp500, access_token)


if __name__ == '__main__':
    main()
