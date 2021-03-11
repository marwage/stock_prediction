from pymongo import MongoClient
import json
import matplotlib.pyplot as plt
import fasttext
import pandas as pd


model = fasttext.load_model("../preprocessing/lid.176.ftz")

def detect_language(text):
    pred = model.predict(text, k=1)
    lang = pred[0][0].replace("__label__", "")
    return lang


def plot_histogram(company, dates):
    num_bins = 240
    fig, axs = plt.subplots()

    axs.hist(dates, bins=num_bins)

    fig.savefig("out/tweet_distr_{}.png".format(company))
    plt.close(fig)


def many():
    client = MongoClient()
    db = client["learning"]

    # for all companies
    tweets_in_english = 0
    tweets_sentiment_zero = 0
    tweets_total = 0
    num_days = 0
    company_stats = []

    company_names = db.list_collection_names()
    for company in company_names:
        # for all days
        company_tweets_in_english = 0
        company_tweets_sentiment_zero = 0
        company_tweets_total = 0
        company_tweets_times = []
        company_num_days = 0

        collection = db[company]
        for day in collection.find():
            # for all tweets
            day_tweets_in_english = 0
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

                text = tweet["text"]
                if detect_language(text) == "en":
                    day_tweets_in_english = day_tweets_in_english + 1

                sentiment = tweet["sentiment"]
                if sentiment == 0:
                    day_tweets_sentiment_zero = day_tweets_sentiment_zero + 1

            company_tweets_in_english = company_tweets_in_english + day_tweets_in_english
            company_tweets_sentiment_zero = company_tweets_sentiment_zero + day_tweets_sentiment_zero
            company_tweets_total = company_tweets_total + day_tweets_total
            company_num_days = company_num_days + 1

        plot_histogram(company, company_tweets_times)
        company_stats.append([company, company_tweets_total, company_tweets_in_english,
                company_tweets_sentiment_zero])

        tweets_in_english = tweets_in_english + company_tweets_in_english
        tweets_sentiment_zero = tweets_sentiment_zero + company_tweets_sentiment_zero
        tweets_total = tweets_total + company_tweets_total
        num_days = num_days + company_num_days
        
    df = pd.DataFrame(company_stats, columns=["company", "num_tweets", "tweets_in_english",
            "tweets_sentiment_zero"])
    df.to_csv("out/company_stats.csv")

    df = pd.DataFrame([[tweets_total, tweets_in_english, tweets_sentiment_zero, num_days,
            len(company_names)]],
            columns=["num_tweets", "tweets_in_english", "tweets_sentiment_zero", "num_days",
                "num_companies"])
    df.to_csv("out/total_stats.csv")


def day_tweet_distr():
    client = MongoClient()
    db = client["learning"]

    #  company_names = ["AAPL"]
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

        fig.savefig("out/tweet_distr_{}.png".format(company))
        plt.close(fig)


def create_json_file():
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
    #  create_json_file()
    #  day_tweet_distr()
    many()


if __name__ == "__main__":
    main()

