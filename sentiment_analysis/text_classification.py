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
    (train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=25000)

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

    # prepare data
    train_data = keras.preprocessing.sequence.pad_sequences(train_data,
                                                            value=word_index["<PAD>"],
                                                            padding='post',
                                                            maxlen=256)

    test_data = keras.preprocessing.sequence.pad_sequences(test_data,
                                                           value=word_index["<PAD>"],
                                                           padding='post',
                                                           maxlen=256)

    # build model
    vocab_size = 25000

    model = keras.Sequential()
    model.add(keras.layers.Embedding(vocab_size, 16))
    model.add(keras.layers.GlobalAveragePooling1D())
    model.add(keras.layers.Dense(16, activation=tf.nn.relu))
    model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['acc'])

    # create validation set 
    x_val = train_data[:10000]
    partial_x_train = train_data[10000:]

    y_val = train_labels[:10000]
    partial_y_train = train_labels[10000:]

    # train model
    history = model.fit(partial_x_train,
                        partial_y_train,
                        epochs=20,
                        batch_size=512,
                        validation_data=(x_val, y_val),
                        verbose=1)

    def word_to_index(word):
        try:
            index = word_index[word]
        except KeyError:
            index = 2
        return index

    #load stocktwits posts
    client = MongoClient()
    db = client["stocktwitsdb"]
    posts = db["AAPL"].find({}, limit=100)
    posts_array = np.zeros((posts.count(), 256))
    for i, post in enumerate(posts):
        text = post["body"]
        text = re.sub(r"\n+", " ", text)
        words_list = re.split(r" ", text)
        words_int = list(map(lambda x: word_to_index(x), words_list))
        posts_array[i, 0:len(words_int)] = words_int

    # prepare data
    predict_data = keras.preprocessing.sequence.pad_sequences(posts_array,
                                                            value=word_index["<PAD>"],
                                                            padding='post',
                                                            maxlen=256)

    # predict
    predictions = model.predict(test_data)

    for i in range(10):
        print(decode_review(test_data[i]))
        print(predictions[i])


if __name__ == '__main__':
  main()
