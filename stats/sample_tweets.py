import datetime
import json
from pymongo import MongoClient


def sample_tweets(company, source: str):
    tweets = company.aggregate([{"$sample": {"size": 10}}])
    for i, tweet in enumerate(tweets):
        del tweet["_id"]
        if "date" in tweet:
            print(type(tweet["date"]))
            if isinstance(tweet["date"], str):
                tweet["date"] = "STRING"
            else:
                tweet["date"] = tweet["date"].isoformat()
        else:
            print("No date key")
            tweet["date"] = "MISSING"

        file_name = "output/sample_{}_{}.json".format(source, i)
        with open(file_name, "w") as tweet_file:
            json.dump(tweet, tweet_file, indent=4)


def main():
    client = MongoClient()

    database = client["stocktwitsdb"]
    company = database["AAPL"]
    sample_tweets(company, "stocktwits")

    database = client["twitterdb"]
    company = database["AAPL"]
    sample_tweets(company, "twitter")


if __name__ == "__main__":
    main()
