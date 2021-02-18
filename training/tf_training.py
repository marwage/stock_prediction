import numpy as np
from pymongo import MongoClient
import tensorflow as tf


def create_dataset(validation_split):
    db_name = "learning"
    collection_name = "AAPL"

    client = MongoClient("localhost", 27017)
    db = client[db_name]

    sentiments = []
    labels = []

    for collection_name in ["AAPL"]:
    #  for collection_name in db.list_collection_names():
        for document in db[collection_name].find({}):
            labels.append(document["price_diff"])
            sentiments.append([pair["sentiment"] for pair in document["tweets"]])

    sentiments = tf.ragged.constant(sentiments)

    labels = tf.constant(labels)

    num_data_samples = len(labels)
    split_point = int(num_data_samples * (1 - validation_split))

    train_dataset = tf.data.Dataset.from_tensor_slices((sentiments[:split_point],
                                                        labels[:split_point]))
    val_dataset = tf.data.Dataset.from_tensor_slices((sentiments[split_point:],
                                                      labels[split_point:]))

    return train_dataset, val_dataset


def main():
    batch_size = 128
    num_hidden_channels = 256
    learning_rate = 0.001
    num_epochs = 10
    validation_split = 0.2

    train_dataset, val_dataset = create_dataset(validation_split)
    train_dataset = train_dataset.shuffle(2048)
    train_dataset = train_dataset.batch(batch_size)
    val_dataset = val_dataset.batch(batch_size)

    print("loading dataset finished")

    # debugging
    for a, b in train_dataset.take(1):
        print(a.shape)
        print(a.dtype)
        print("+++")
        print(b.shape)
        print(b.dtype)
        break

    model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=(None,), dtype=tf.float32, ragged=True),
        tf.keras.layers.Reshape((None, None, 1)),
        tf.keras.layers.LSTM(num_hidden_channels),
        tf.keras.layers.Dense(1)
        ])

    model.compile(loss=tf.keras.losses.MeanAbsoluteError,
                  optimizer=tf.keras.optimizers.Adam(learning_rate))

    print(model.summary())

    model.fit(train_dataset, epochs=num_epochs, validation_data=val_dataset)


if __name__ == "__main__":
    main()

