import tensorflow as tf
from tensorflow import keras
import numpy as np

print("tf.version: " + str(tf.__version__))

# load imdb dataset
imdb = keras.datasets.imdb
(train_data, train_labels), (test_data, test_labels) = imdb.load_data()

print("training entries: {}, labels: {}".format(len(train_data), len(train_labels)))

print("first entry in train_data: " + str(train_data[0]))

print("length of first entry in train_data: " + str(len(train_data[0])))
print("length of second entry in train_data: "+ str(len(train_data[1])))

# dictionary mapping words to an integer index
word_index = imdb.get_word_index()

# The first indices are reserved
word_index = {k:(v+3) for k,v in word_index.items()}
word_index["<PAD>"] = 0
word_index["<START>"] = 1
word_index["<UNK>"] = 2  # unknown
word_index["<UNUSED>"] = 3

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

def decode_review(text):
    return ' '.join([reverse_word_index.get(i, '?') for i in text])

print("train_data[0] decoded: " + str(decode_review(train_data[0])))

