import tensorflow as tf
from tensorflow import keras
import numpy as np
from pymongo import MongoClient
import re


def words_to_index(word_index, words):
    words_int = []
    for word in words:
        try:
            index = word_index[word]
        except KeyError:
            index = 2
        words_int.append(index)

    return words_int


def main():
    #load stocktwits posts
    client = MongoClient()
    db = client["stocktwitsdb"]
    posts = db["AAPL"].find({}, limit=5)
    posts_array = np.zeros((posts.count(), 256))
    for i, post in enumerate(posts):
        text = post["body"]
        print(text)
        text = re.sub(r"\n+", " ", text)
        word_list = re.split(r" ", text)
        words_int = words_to_index(word_index, word_list)
        print(words_int)
        posts_array[i, 0:len(words_int)]
        print(posts_array[i])


if __name__ == '__main__':
  main()
