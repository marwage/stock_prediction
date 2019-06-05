import numpy as np
import json
import twitter
from datetime import date, timedelta
from pymongo import MongoClient


def read_sp500(path):
    sp500 = np.genfromtxt(path, dtype=None, delimiter=",", names=True, encoding="utf8")
    filter = sp500[:]["conm"]=="S&P 500 Comp-Ltd"
    sp500 = sp500[filter]
    filter = sp500[:]["thru"]==""
    sp500 = sp500[filter]
    
    return sp500


def query_store(sp500):
    #mongodb
    client = MongoClient()
    db = client.twitterdb
    #twitter
    with open("files/access_token.json") as access_token_file:
        json_object = json.load(access_token_file)
    api = twitter.Api(consumer_key=json_object["consumer_key"],
                  consumer_secret=json_object["consumer_secret"],
                  access_token_key=json_object["access_token_key"],
                  access_token_secret=json_object["access_token_secret"])

    companies = sp500["co_tic"].tolist()

    for company in companies:
        collection = db.aapl

        company_abbreviation = "aapl"
        since = date.today() - timedelta(days=1)
        until = date.today()
        query = "q=" + company_abbreviation + "%20since%3A" + str(since) + "%20until%3A" + str(until)
        results = api.GetSearch(raw_query=query)
        for tweet in results:
            tweet_json = json.loads(str(tweet))
            tweet_id = collection.insert_one(tweet_json).inserted_id


def main():
    path = "files/sp500_constituents.csv"

    sp500 = read_sp500(path)
    query_store(sp500)


if __name__ == '__main__':
    main()