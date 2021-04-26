import datetime
import json
import logging
import os
import pymongo
import sys
import tensorflow as tf
from pathlib import Path


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


def convert_dict_to_list(dictionary):
    new_list = []
    for key, value in dictionary.items():
        new_list.append(value)
    return new_list


def get_list_with_zeros(num):
    return [0.0 for i in range(num)]


def create_tf_data_set():
    client = pymongo.MongoClient()
    database = client["trainingdatasetdb"]
    collection = database["Ava"]
    cursor = collection.find(batch_size=64)

    input_tweets = []
    input_ideas = []
    input_company_infos = []
    labels = []

    for day in cursor:
        tweets = day["tweets"]
        tweets = filter_tweets(tweets)
        for tweet in tweets:
            tweet.pop("language")
        tweets_list = [convert_dict_to_list(tweet) for tweet in tweets]

        ideas = day["ideas"]
        ideas = filtered_ideas(ideas)
        ideas_list = [convert_dict_to_list(idea) for idea in ideas]

        num_tweets = len(tweets_list)
        num_ideas = len(ideas_list)
        if num_tweets == 0 and num_ideas == 0:
            continue
        if num_tweets == 0:
            tweets_list = [get_list_with_zeros(10)]
        if num_ideas == 0:
            ideas_list = [get_list_with_zeros(9)]

        company_info = day["company_info"]
        company_info_list = convert_dict_to_list(company_info)

        input_tweets.append(tweets_list)
        input_ideas.append(ideas_list)
        input_company_infos.append(company_info_list)
        labels.append(day["price_diff"])

    tf_tweets = tf.ragged.constant(input_tweets, inner_shape=(10,))
    tf_ideas = tf.ragged.constant(input_ideas, inner_shape=(9,))
    tf_company_infos = tf.constant(input_company_infos)
    tf_lables = tf.constant(labels)

    input_dict = {"tweets": tf_tweets,
                  "ideas": tf_ideas,
                  "company_info": tf_company_infos}
    data_set = tf.data.Dataset.from_tensor_slices((input_dict, tf_lables))
    return data_set


def main():
    if sys.platform == "linux":
        base_path = os.path.join(Path.home(), "stock/stock-prediction")
    else:
        path = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        base_path = os.path.join(Path.home(), path)

    path = "training/log/create_tf_data_set.log"
    logging_path = os.path.join(base_path, path)
    logging.basicConfig(
        filename=logging_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    data_set = create_tf_data_set()

    logging.info("element_spec: %s", data_set.element_spec)
    print("element_spec: {}".format(data_set.element_spec))

    data_set_path = os.path.join(base_path, "training/dataset/Ava")
    tf.data.experimental.save(data_set, data_set_path)


if __name__ == "__main__":
    main()
