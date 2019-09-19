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
    # download imdb dataset
    imdb = keras.datasets.imdb

    # dictionary mapping words to an integer index
    word_index = imdb.get_word_index()

    # The first indices are reserved
    word_index = {k:(v+3) for k,v in word_index.items()}
    word_index["<PAD>"] = 0
    word_index["<START>"] = 1
    word_index["<UNK>"] = 2  # unknown
    word_index["<UNUSED>"] = 3

    #load stocktwits posts
    client = MongoClient()
    db = client["stocktwitsdb"]
    posts = db["AAPL"].find({}, limit=1)
    posts_array = np.zeros((posts.count(), 256))
    for i, post in enumerate(posts):
        text = post["body"]
        text = re.sub(r"\n+", " ", text)
        word_list = re.split(r" ", text)
        words_int = words_to_index(word_index, word_list)
        posts_array[i, 0:len(words_int)] = words_int
        for i in range(5):
            print(text)
            print(posts_array[i])


if __name__ == '__main__':
  main()
