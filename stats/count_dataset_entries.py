import json
import matplotlib.pyplot as plt
import os
import pandas as pd
from pymongo import MongoClient


def plot_histogram(company: str, dates, output_path: str):
    num_bins = 240
    fig, ax = plt.subplots()
    ax.set_xlabel("Hour")
    ax.set_ylabel("Number of tweets")

    ax.hist(dates, bins=num_bins)

    file_name = os.path.join(output_path, "tweet_distr_{}.png".format(company))
    fig.savefig(file_name)
    plt.close(fig)


def count_dataset_entries(output_path: str):
    client = MongoClient()
    db = client["learning"]

    # for all companies
    tweets_sentiment_zero = 0
    tweets_total = 0
    num_days = 0
    company_stats = []

    #  company_names = db.list_collection_names()
    company_names = ["AAPL"]
    for company in company_names:
        # for all days
        company_tweets_sentiment_zero = 0
        company_tweets_total = 0
        company_tweets_times = []
        company_num_days = 0

        collection = db[company]
        for day in collection.find():
            # for all tweets
            day_tweets_sentiment_zero = 0
            day_tweets_total = 0

            tweets = day["tweets"]
            for tweet in tweets:
                # for each tweet
                day_tweets_total = day_tweets_total + 1

                date = tweet["date"]
                d = date.hour + date.minute / 60
                # shift
                if d >= 14.5:
                    d = d - 14.5
                else:
                    d = d + 9.5
                company_tweets_times.append(d)

                sentiment = tweet["sentiment"]
                if sentiment == 0:
                    day_tweets_sentiment_zero = day_tweets_sentiment_zero + 1

            company_tweets_sentiment_zero = (company_tweets_sentiment_zero
                                             + day_tweets_sentiment_zero)
            company_tweets_total = company_tweets_total + day_tweets_total
            company_num_days = company_num_days + 1

        plot_histogram(company, company_tweets_times, output_path)
        company_stats.append([company, company_tweets_total,
                              company_tweets_sentiment_zero])

        tweets_sentiment_zero = (tweets_sentiment_zero
                                 + company_tweets_sentiment_zero)
        tweets_total = tweets_total + company_tweets_total
        num_days = num_days + company_num_days

    df = pd.DataFrame(company_stats,
                      columns=["company", "num_tweets",
                               "tweets_sentiment_zero"])
    file_name = os.path.join(output_path, "company_stats.csv")
    df.to_csv(file_name)

    df = pd.DataFrame([[tweets_total, tweets_sentiment_zero,
                        num_days, len(company_names)]],
                      columns=["num_tweets", "tweets_sentiment_zero",
                               "num_days", "num_companies"])
    file_name = os.path.join(output_path, "total_stats.csv")
    df.to_csv(file_name)


def day_tweet_distr(output_path: str):
    client = MongoClient()
    db = client["learning"]

    company_names = db.list_collection_names()
    num_bins = 240

    for company in company_names:
        x = []
        collection = db[company]
        for day in collection.find():
            tweets = day["tweets"]
            for tweet in tweets:
                date = tweet["date"]
                d = date.hour + date.minute / 60
                x.append(d)

        fig, axs = plt.subplots()

        axs.hist(x, bins=num_bins)

        file_name = os.path.join(output_path,
                                 "tweet_distr_{}.png".format(company))
        fig.savefig(file_name)
        plt.close(fig)


def create_json_file(output_path: str):
    client = MongoClient()
    learning_db = client["learning"]

    collection_names = learning_db.list_collection_names()
    num_companies = len(collection_names)
    print("Number of companies: {}".format(num_companies))

    stats = dict()
    for company in collection_names:
        collection = learning_db[company]
        stats[company] = dict()

        stats[company]["days"] = collection.count_documents({})

        tweets = list()
        for day in collection.find():
            tweets.append(len(day["tweets"]))
        stats[company]["tweets"] = tweets

    with open("stats.json", "w") as json_file:
        json.dump(stats, json_file, indent=4)


def main():
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)

    count_dataset_entries(output_path)


if __name__ == "__main__":
    main()
