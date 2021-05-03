import argparse
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
from requests_oauthlib import OAuth1
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def read_bearer_token(bearer_token_path: str):
    with open(bearer_token_path, "r") as bearer_token_file:
        json_object = json.load(bearer_token_file)
    return json_object["bearer_token"]


def read_finished_companies(path):
    with open(path, "r") as companies_file:
        finished_companies = json.load(companies_file)

    return finished_companies


def write_finished_companies(path, finished_companies):
    with open(path, "w") as companies_file:
        json.dump(finished_companies, companies_file, indent=4)


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


def request_until_success(headers: dict, params: dict):
    timeout = 30
    search_url = "https://api.twitter.com/2/tweets/search/all"
    succeeded = False
    while not succeeded:
        try:
            result = requests.get(search_url,
                                  headers=headers,
                                  params=params,
                                  timeout=timeout)
        except Exception as e:
            logging.warning(str(e))
            continue

        status_code = result.status_code
        if not status_code == 200:
            if status_code == 429:
                logging.info("Sleeping for 15 min")
                time.sleep(905)

            continue

        succeeded = True
        result_json = result.json()

        if "errors" in result_json:
            errors = dict()
            for error in result_json["errors"]:
                error_title = error["title"]
                if error_title in errors:
                    errors[error_title] = errors[error_title] + 1
                else:
                    errors[error_title] = 1
            logging.info("Request errors: %s", json.dumps(errors))

    return result_json


def crawl_company(company: str, database, headers: dict):
    hastag_code = "#"
    cashtag_code = "$"
    if args.onlycashtag:
        tags = [cashtag_code]
    else:
        tags = [hastag_code, cashtag_code]
    first_date = datetime.datetime(2019, 4, 1)
    start_time = first_date.isoformat(timespec="milliseconds")
    start_time = start_time + "Z"

    for tag in tags:
        has_next_token = True
        next_token = None
        num_next_token = 0
        while has_next_token:
            query = "{}{} lang:en".format(tag, company)
            params = construct_params(query, start_time)
            if next_token is not None:
                params["next_token"] = next_token

            result = request_until_success(headers, params)

            if "data" not in result:
                logging.warning("Response error: %s", result["error"])
                continue
            tweets = result["data"]

            logging.info("%d results for %s, next token %d",
                         len(tweets), company, num_next_token)

            collection = database[company]
            for tweet in tweets:
                created_at = re.sub("Z", "", tweet["created_at"])
                date = datetime.datetime.fromisoformat(created_at)
                tweet["date"] = date

                if tag == hastag_code:
                    tweet["tag"] = "hastag"
                else:  # tag == cashtag_code
                    tweet["tag"] = "cashtag"

                collection.update_one({"id": tweet["id"]},
                                      {"$set": tweet},
                                      upsert=True)

            if "next_token" in result["meta"]:
                next_token = result["meta"]["next_token"]
                num_next_token = num_next_token + 1
            else:
                has_next_token = False


def crawl_twitter(sp500: list,
                  bearer_token: str,
                  finished_companies_path: str):
    client = MongoClient()
    database = client["twitterv2db"]
    headers = {"Authorization": "Bearer " + bearer_token}

    finished_companies = read_finished_companies(finished_companies_path)

    while True:
        for company in sp500:
            if company in finished_companies:
                continue

            crawl_company(company, database, headers)

            finished_companies.append(company)
            write_finished_companies(finished_companies_path,
                                     finished_companies)


def main():
    sp500_path = os.path.join(".", "data/sp500.json")
    finished_companies_path = os.path.join(".",
                                           "data/finished_companies.json")
    log_path = os.path.join(".", "log/twitter_v2_academic.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    bearer_token_path = os.path.join(".",
                                     "access_token/twitter_bearer_token.json")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    random.shuffle(sp500)
    bearer_token = read_bearer_token(bearer_token_path)

    crawl_twitter(sp500, bearer_token, finished_companies_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training parameters")
    parser.add_argument("--onlycashtag", action="store_true",
                        help="Only Cashtag $")
    args = parser.parse_args()

    main()
