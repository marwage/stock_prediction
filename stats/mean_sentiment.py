import os
import pandas as pd
from datetime import datetime
from pymongo import MongoClient


def extract_mean_sentiment(output_path: str, only_nonzero: bool):
    client = MongoClient()
    database = client["twitter_three"]

    threshold_date = datetime(2020, 1, 1)

    company_names = database.list_collection_names()
    for company in company_names:
        mean_sentiments = []

        collection = database[company]
        days = collection.find()
        for day in days:
            start_date = day["start"]
            if start_date < threshold_date:
                continue

            day_sum_sentiment = 0
            day_num_tweets = 0

            tweets = day["tweets"]
            for tweet_features in tweets:
                sentiment = tweet_features[0]
                if (only_nonzero and sentiment != 0) or not only_nonzero:
                    day_sum_sentiment = day_sum_sentiment + sentiment
                    day_num_tweets = day_num_tweets + 1

            start_date_str = "{}-{}-{}".format(start_date.year,
                                               start_date.month,
                                               start_date.day)
            mean_sentiment = day_sum_sentiment / day_num_tweets
            mean_sentiments.append([start_date_str, mean_sentiment])

        data_frame = pd.DataFrame(mean_sentiments,
                                  columns=["date", "mean_sentiment"])
        if only_nonzero:
            file_name = "mean_sentiments_nonzero_{}.csv".format(company)
        else:
            file_name = "mean_sentiments_{}.csv".format(company)
        file_name = os.path.join(output_path, file_name)
        data_frame.to_csv(file_name)


def main():
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)

    only_nonzero = True
    extract_mean_sentiment(output_path, only_nonzero)

    only_nonzero = False
    extract_mean_sentiment(output_path, only_nonzero)


if __name__ == "__main__":
    main()
