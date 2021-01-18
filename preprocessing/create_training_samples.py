import json
import matplotlib.pyplot as plt
import numpy as np
import logging
from pymongo import MongoClient
from datetime import datetime
import os
from pathlib import Path

def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def create_training_samples():
    client = MongoClient()
    learning_db = client["learning"]
    twitter_db = client["twitter"]
    stocktwits_db = client["stocktwits"]

    sp500_path = os.path.join(Path.home(),  "stock-prediction/crawling/data/sp500.json")
    sp500 = read_sp500(sp500_path)
    
    print(sp500)
    return

    for company in sp500:
        logging.debug("get posts of " + company)
        collection = db[company]
        company_stats = dict()
        for post in collection.find({}):
            date_string = post["created_at"]
            if db_name == "stocktwitsdb":
                post_date = datetime.strptime(date_string[0:10], "%Y-%m-%d")
            elif db_name == "twitterdb":
                post_date = datetime.strptime(date_string, "%a %b %d %H:%M:%S %z %Y")
            else:
                logging.error("database not found")
            date_string = post_date.strftime('%Y-%m-%d')
            if date_string in company_stats:
                company_stats[date_string] = company_stats[date_string] + 1
            else:
                company_stats[date_string] = 1
        plot_company_stats(db_name, company, company_stats)


def main():
    # log_path = ""
    # logging.basicConfig(
    #     filename=log_path,
    #     level=logging.DEBUG,
    #     format="%(asctime)s:%(levelname)s:%(message)s"
    #     )

    create_training_samples()


if __name__ == '__main__':
    main()
