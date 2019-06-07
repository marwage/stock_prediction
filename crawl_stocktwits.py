import numpy as np
import json
import time
import requests
from datetime import date, timedelta, datetime
from pymongo import MongoClient

files_path = "/home/wagenlaeder/stock-prediction/files"
log_file = "crawl_stocktwits.log"

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

    companies = sp500["co_tic"].tolist()

    for company in companies:
        since = date.today() - timedelta(days=1)
        until = date.today()
        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"
        exceeded = True
        while exceeded:
            result = requests.get(request_url)
            print(result.status_code)
            if result.status_code == 200:
                exceeded = False
            if result.status_code == 429:
                # log
                with open(files_path + log_file, "a") as log:
                    log.write("sleeping for 16 min\n")
                time.sleep(3660)

        # log
        with open(files_path + log_file, "a") as log:
            log.write(str(len(results)) + " results for " + company + "\n")

        collection = db[company]
        for post in result.json()["messages"]:
            write_result = collection.update(post, post, upsert=True)


def main():
    path = files_path + "/sp500_constituents.csv"

    sp500 = read_sp500(path)
    query_store(sp500)

    # log
    with open(files_path + log_file, "a") as log:
        log.write(str(datetime.now()) + " finished\n")


if __name__ == '__main__':
    main()
