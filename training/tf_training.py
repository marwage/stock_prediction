from pymongo import MongoClient
import tensorflow as tf
import datetime


def create_dataset(validation_split):
    db_name = "learning"

    client = MongoClient("localhost", 27017)
    db = client[db_name]

    sentiments = []
    labels = []

    for collection_name in db.list_collection_names():
        for document in db[collection_name].find({}):
            labels.append(document["price_diff"])
            sentiments.append([[pair["sentiment"]] for pair in document["tweets"]])
            # data must be 3D for LSTM

    sentiments = tf.ragged.constant(sentiments, inner_shape=(1,))

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
    num_hidden_channels = 64
    learning_rate = 0.001
    num_epochs = 10
    validation_split = 0.2

    train_dataset, val_dataset = create_dataset(validation_split)
    train_dataset = train_dataset.shuffle(2048)
    train_dataset = train_dataset.batch(batch_size)
    val_dataset = val_dataset.batch(batch_size)

    print("loading dataset finished")

    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(num_hidden_channels),
        tf.keras.layers.Dense(1)
        ])

    model.compile(loss=tf.keras.losses.MeanSquaredError(),
                  optimizer=tf.keras.optimizers.Adam(learning_rate))

    log_dir = "logs/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    model.fit(train_dataset,
            epochs=num_epochs,
            validation_data=val_dataset,
            callbacks=[tensorboard_callback])

    print(model.summary())


if __name__ == "__main__":
    main()

