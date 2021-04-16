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


def read_bearer_token(bearer_token_path):
    with open(bearer_token_path, "r") as bearer_token_file:
        json_object = json.load(bearer_token_file)
    return json_object["bearer_token"]


def crawl_twitter(sp500, bearer_token):
    client = MongoClient()
    database = client["twitterv2"]

    headers = {"Authorization": "Bearer " + bearer_token}
    api_url = "https://api.twitter.com/2/tweets/search/recent?"
    expansions = "&expansions=attachments.poll_ids,attachments.media_keys," \
        + "author_id,entities.mentions.username,geo.place_id," \
        + "in_reply_to_user_id,referenced_tweets.id," \
        + "referenced_tweets.id.author_id"
    max_results = "&max_results=100"
    place_fields = "&place.fields=contained_within,country,country_code," \
        + "full_name,geo,id,name,place_type"
    tweet_fields = "&tweet.fields=attachments,author_id,context_annotations," \
        + "conversation_id,created_at,entities,geo,id,in_reply_to_user_id," \
        + "lang,non_public_metrics,public_metrics,organic_metrics," \
        + "promoted_metrics,possibly_sensitive,referenced_tweets," \
        + "reply_settings,source,text,withheld"
    user_fields = "&user.fields=created_at,description,entities,id,location," \
        + "name,pinned_tweet_id,profile_image_url,protected,public_metrics," \
        + "url,username,verified,withheld"

    while True:
        for company in sp500:
            query = "query=%23" + company
            url = api_url + query + expansions + max_results + place_fields \
                + tweet_fields + user_fields

            succeeded = False
            while not succeeded:
                try:
                    result = requests.get(url, headers=headers)
                    result_json = result.json()

                    # debugging
                    with open("result.json", "w") as result_file:
                        json.dump(result_json, result_file, indent=4)
                    return

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
    log_path = os.path.join(crawling_path, "log/twitter_v2_enterprise.log")
    bearer_token_path = os.path.join(crawling_path,
                                     "access_token/twitter_bearer_token.json")

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    #  logging.getLogger("requests").setLevel(logging.WARNING)
    #  logging.getLogger("urllib3").setLevel(logging.WARNING)
    #  logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    bearer_token = read_bearer_token(bearer_token_path)
    crawl_twitter(sp500, bearer_token)


if __name__ == '__main__':
    main()
