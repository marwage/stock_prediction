import numpy as np
import json
import twitter
import time
from datetime import date, timedelta, datetime
from pymongo import MongoClient

files_path = "/home/wagenlaeder/stock-prediction/files"

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
    db = client.stocktwitsdb
    #twitter
    with open(files_path + "/access_token.json") as access_token_file:
        json_object = json.load(access_token_file)
    api = twitter.Api(consumer_key=json_object["consumer_key"],
                  consumer_secret=json_object["consumer_secret"],
                  access_token_key=json_object["access_token_key"],
                  access_token_secret=json_object["access_token_secret"])

    companies = sp500["co_tic"].tolist()

    for company in companies:
        since = date.today() - timedelta(days=1)
        until = date.today()
        query = "q=" + "%24"+ company + "%20since%3A" + str(since) + "%20until%3A" + str(until)
        exceeded = True
        while exceeded:
            try:
                results = api.GetSearch(raw_query=query)
                exceeded = False
            except:
                # log
                with open(files_path + "/crawl_twitter.log", "a") as log:
                    log.write("sleeping for 16 min\n")
                time.sleep(960)

        # log
        with open(files_path + "/crawl_twitter.log", "a") as log:
            log.write(str(len(results)) + " results for " + company + "\n")

        collection = db[company]
        for tweet in results:
            tweet_json = json.loads(str(tweet))
            write_result = collection.update(tweet_json, tweet_json, upsert=True)


def main():
    path = files_path + "/sp500_constituents.csv"

    sp500 = read_sp500(path)
    query_store(sp500)

    # log
    with open(files_path + "/crawl_twitter.log", "a") as log:
        log.write(str(datetime.now()) + " finished\n")


if __name__ == '__main__':
    main()
