import json
import time
import requests
from requests_oauthlib import OAuth1


def read_access_token(access_token_path):
    with open(access_token_path, "r") as access_token_file:
        access_token = json.load(access_token_file)

    return access_token


def crawl_twitter(access_token):
    auth = OAuth1(access_token["consumer_key"], access_token["consumer_secret"],
        access_token["access_token_key"], access_token["access_token_secret"])

    company = "AAPL"

    query_dollar = "https://api.twitter.com/1.1/search/tweets.json?q=" + "%24"+ company + "&result_type=recent&count=100"
    query_hashtag = "https://api.twitter.com/1.1/search/tweets.json?q=" + "%23"+ company + "&result_type=recent&count=100"
    queries = [query_dollar, query_hashtag]

    for query in queries:
        succeeded = False
        while not succeeded:
            try:
                result = requests.get(query, auth=auth)
                succeeded = True
            except:
                print("sleeping for 15 min")
                time.sleep(900)

        print(result.json())


def main():
    crawling_path = "stock-prediction/crawling/"
    sp500_path = crawling_path + "data/sp500.json"
    log_path = crawling_path + "log/test_twitter_api.log"
    access_token_path = crawling_path + "access_token/twitter_access_token.json"

    access_token = read_access_token(access_token_path)
    crawl_twitter(access_token)


if __name__ == '__main__':
    main()
