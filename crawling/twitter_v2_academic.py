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
from read_sp500 import read_sp500
from requests_oauthlib import OAuth1


def read_bearer_token(bearer_token_path: str):
    with open(bearer_token_path, "r") as bearer_token_file:
        json_object = json.load(bearer_token_file)
    return json_object["bearer_token"]


def construct_params(query: str, start_time: str):
    params = {"query": query,
              "max_results": 500,
              "start_time":  start_time}

    params["expansions"] = "attachments.poll_ids,attachments.media_keys," \
        + "author_id,entities.mentions.username,geo.place_id," \
        + "in_reply_to_user_id"
    params["place.fields"] = "contained_within,country,country_code," \
        + "full_name,geo,id,name,place_type"
    params["tweet.fields"] = "attachments,author_id,context_annotations," \
        + "conversation_id,created_at,entities,geo,id,in_reply_to_user_id," \
        + "lang,public_metrics,possibly_sensitive,referenced_tweets," \
        + "reply_settings,source,text,withheld"
    params["user.fields"] = "created_at,description,entities,id,location," \
        + "name,pinned_tweet_id,profile_image_url,protected,public_metrics," \
        + "url,username,verified,withheld"

    return params


def construct_header(bearer_token: str):
    return {"Authorization": "Bearer {}".format(bearer_token)}


def request_until_seccess(headers: dict, params: dict):
    search_url = "https://api.twitter.com/2/tweets/search/all"
    succeeded = False
    while not succeeded:
        result = requests.get(search_url,
                              headers=headers,
                              params=params)

        status_code = result.status_code
        if not status_code == 200:
            logging.warning("Status code is %d", status_code)
            if status_code == 503:
                continue
            if status_code == 429:
                time.sleep(905)
                continue

        try:
            result_json = result.json()
            succeeded = True
        except Exception as e:
            logging.warning(str(e))

        if "errors" in result_json:
            logging.info("%d errors in result", len(result_json["errors"]))

    return result_json


def crawl_company(company: str, database, headers: dict):
    hastag_code = "#"
    cashtag_code = "$"
    tags = [hastag_code, cashtag_code]
    first_date = datetime.datetime(2019, 4, 1)
    start_time = first_date.isoformat(timespec="milliseconds")
    start_time = start_time + "Z"

    for tag in tags:
        query = "{}{} lang:en".format(tag, company)
        params = construct_params(query, start_time)

        result = request_until_seccess(headers, params)

        # debugging
        with open("result.json", "w") as result_file:
            json.dump(result, result_file, indent=4)

        if "data" not in result:
            logging.warning("%s", result["error"])
            continue
        tweets = result["data"]

        logging.info("%d results for %s", len(tweets), company)

        collection = database[company]
        for tweet in tweets:
            created_at = re.sub("Z", "", tweet["created_at"])
            date = datetime.datetime.fromisoformat(created_at)
            tweet["date"] = date

            if tag == hastag_code:
                tweet["tag"] = "hastag"
            else:  # tag == cashtag_code
                tweet["tag"] = "cashtag"

            db_query = {
                "text": tweet["text"],
                "date": date
                }
            collection.update_one(db_query,
                                  {"$set": tweet},
                                  upsert=True)


def crawl_twitter(sp500: list, bearer_token: str):
    client = MongoClient()
    database = client["twitterv2db"]
    headers = {"Authorization": "Bearer " + bearer_token}

    while True:
        for company in sp500:
            crawl_company(company, database, headers)


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        directory = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        path = os.path.join(Path.home(), directory)
    crawling_path = os.path.join(path, "crawling")
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    log_path = os.path.join(crawling_path, "log/twitter_v2_enterprise.log")
    bearer_token_path = os.path.join(crawling_path,
                                     "access_token/twitter_bearer_token.json")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        #  level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    random.shuffle(sp500)
    bearer_token = read_bearer_token(bearer_token_path)

    crawl_twitter(sp500, bearer_token)


if __name__ == '__main__':
    main()
