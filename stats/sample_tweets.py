import datetime
import json
import os
from pymongo import MongoClient


def sample_tweets(company, source: str, output_path: str):
    tweets = company.aggregate([{"$sample": {"size": 10}}])
    for i, tweet in enumerate(tweets):
        del tweet["_id"]
        if "date" in tweet:
            if isinstance(tweet["date"], str):
                tweet["date"] = "STRING"
            else:
                tweet["date"] = tweet["date"].isoformat()
        else:
            tweet["date"] = "MISSING"

        file_name = "sample_{}_{}.json".format(source, i)
        file_name = os.path.join(output_path, file_name)
        with open(file_name, "w") as tweet_file:
            json.dump(tweet, tweet_file, indent=4)


def main():
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)

    client = MongoClient()

    database = client["stocktwitsdb"]
    company = database["AAPL"]
    sample_tweets(company, "stocktwits", output_path)

    database = client["twitterdb"]
    company = database["AAPL"]
    sample_tweets(company, "twitter", output_path)


if __name__ == "__main__":
    main()
