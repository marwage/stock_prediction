import numpy as np
import json
import twitter
import time
import logging
from datetime import date, timedelta, datetime
from pymongo import MongoClient
from read_sp500 import read_sp500


def crawl_twitter(sp500, access_token_path):
    client = MongoClient()
    db = client.twitterdb

    with open(access_token_path, "r") as access_token_file:
        json_object = json.load(access_token_file)

    api = twitter.Api(consumer_key=json_object["consumer_key"],
                  consumer_secret=json_object["consumer_secret"],
                  access_token_key=json_object["access_token_key"],
                  access_token_secret=json_object["access_token_secret"])

    for company in sp500:
        since = date.today() - timedelta(days=1)
        until = date.today()
        query = "q=" + "%24"+ company + "%20since%3A" + str(since) + "%20until%3A" + str(until)
        succeeded = False
        while not succeeded:
            try:
                results = api.GetSearch(raw_query=query)
                succeeded = True
            except:
                log.debug("sleeping for 16 min")
                time.sleep(960)

        logging.debug(str(len(results)) + " results for " + company)

        collection = db[company]
        for tweet in results:
            tweet_json = json.loads(str(tweet))
            query = {
                    "text": post["text"],
                    "created_at": post["created_at"]
                    }
            write_result = collection.update(query, tweet_json, upsert=True)


def main():
    crawling_path = "stock-prediction/crawling/"
    sp500_path = crawling_path + "data/sp500.json"
    log_path = crawling_path + "log/crawl_stocktwits.log"
    access_token_path = crawling_path + "access_token/twitter_access_token.json"

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    logging.info("start crawling twitter")

    sp500 = read_sp500(path)
    crawl_twitter(sp500, access_token_path)

    logging.info("crawling twitter finished")


if __name__ == '__main__':
    main()
