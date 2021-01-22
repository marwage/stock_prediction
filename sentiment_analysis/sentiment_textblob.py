from textblob import TextBlob
from pymongo import MongoClient
import json
import os
from pathlib import Path


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]

def sentiment():
    client = MongoClient()
    learning_db = client["learning"]

    sp500_path = os.path.join(Path.home(),
            "Studies/Master/10SS19/StockPrediction/stock-prediction/crawling/data/sp500.json")
    sp500 = read_sp500(sp500_path)

    for company in sp500:
        company_coll = learning_db[company]

        day = company_coll.find_one()
        if day is not None:
            tweets = day["tweets"]
            text = TextBlob(tweets[0]["text"])
            sentiment = text.sentiment.polarity
            if sentiment != 0.0:
                print(text)
                print(sentiment)
                print("---")

def main():
    sentiment()


if __name__ == "__main__":
    main()
