import logging
import os
import pandas as pd
import pymongo


def filter_tweets(tweets):
    filtered_tweets = []
    for tweet in tweets:
        if (tweet["sentiment_polarity"] != 0.0
                and tweet["sentiment_subjectivity"] != 0.0
                and tweet["language"] == "en"):
            filtered_tweets.append(tweet)
    return filtered_tweets


def filter_ideas(ideas):
    filtered_ideas = []
    for idea in ideas:
        if (idea["sentiment_polarity"] != 0.0
                and idea["sentiment_subjectivity"] != 0.0):
            filtered_ideas.append(idea)
    return filtered_ideas


def sum_sentiment(tweets):
    if len(tweets) == 0:
        return 0.0, 0.0

    sum_polarity = 0.0
    sum_subjectivity = 0.0
    for tweet in tweets:
        sum_polarity = sum_polarity + tweet["sentiment_polarity"]
        sum_subjectivity = sum_subjectivity + tweet["sentiment_subjectivity"]

    return sum_polarity, sum_subjectivity


def calculate_mean(summ: float, num: int):
    if num == 0:
        return 0.0

    return summ / float(num)


def retrieve_sentiment(output_path: str):
    client = pymongo.MongoClient()
    database = client["trainingdatasetdb"]
    collection = database["Ava"]
    cursor = collection.find(batch_size=64)

    sentiment = dict()

    for day in cursor:
        tweets = day["tweets"]
        tweets = filter_tweets(tweets)
        num_tweets = len(tweets)
        summ = sum_sentiment(tweets)
        tweets_polarity_sum, tweets_subjectivity_sum = summ
        tweets_polarity_mean = calculate_mean(tweets_polarity_sum, num_tweets)
        tweets_subjectivity_mean = calculate_mean(tweets_subjectivity_sum,
                                                  num_tweets)

        ideas = day["ideas"]
        ideas = filter_ideas(ideas)
        num_ideas = len(ideas)
        summ = sum_sentiment(ideas)
        ideas_polarity_sum, ideas_subjectivity_sum = summ
        ideas_polarity_mean = calculate_mean(ideas_polarity_sum, num_ideas)
        ideas_subjectivity_mean = calculate_mean(ideas_subjectivity_sum, num_ideas)

        company = day["company"]
        if company not in sentiment:
            sentiment[company] = dict()
            sentiment[company]["date"] = []
            sentiment[company]["tweets_sentiment_polarity_sum"] = []
            sentiment[company]["tweets_sentiment_subjectivity_sum"] = []
            sentiment[company]["tweets_sentiment_polarity_mean"] = []
            sentiment[company]["tweets_sentiment_subjectivity_mean"] = []
            sentiment[company]["tweets_count"] = []
            sentiment[company]["ideas_sentiment_polarity_sum"] = []
            sentiment[company]["ideas_sentiment_subjectivity_sum"] = []
            sentiment[company]["ideas_sentiment_polarity_mean"] = []
            sentiment[company]["ideas_sentiment_subjectivity_mean"] = []
            sentiment[company]["ideas_count"] = []
            sentiment[company]["price_diff"] = []
        else:
            sentiment[company]["date"].append(day["start"])
            sentiment[company]["tweets_sentiment_polarity_sum"].append(tweets_polarity_sum)
            sentiment[company]["tweets_sentiment_subjectivity_sum"].append(tweets_subjectivity_sum)
            sentiment[company]["tweets_sentiment_polarity_mean"].append(tweets_polarity_mean)
            sentiment[company]["tweets_sentiment_subjectivity_mean"].append(tweets_subjectivity_mean)
            sentiment[company]["tweets_count"].append(num_tweets)
            sentiment[company]["ideas_sentiment_polarity_sum"].append(ideas_polarity_sum)
            sentiment[company]["ideas_sentiment_subjectivity_sum"].append(ideas_subjectivity_sum)
            sentiment[company]["ideas_sentiment_polarity_mean"].append(ideas_polarity_mean)
            sentiment[company]["ideas_sentiment_subjectivity_mean"].append(ideas_subjectivity_mean)
            sentiment[company]["ideas_count"].append(num_ideas)
            sentiment[company]["price_diff"].append(day["price_diff"])

    for key, value in sentiment.items():
        data_frame = pd.DataFrame(value)
        file_name = "sentiment_{}.csv".format(key)
        data_frame.to_csv(os.path.join(output_path, file_name))


def main():
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)
    log_path = os.path.join(".", "log/sentiment.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    retrieve_sentiment(output_path)


if __name__ == "__main__":
    main()
