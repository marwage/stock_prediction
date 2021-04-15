import argparse
import datetime
import os
import optuna
from optuna.integration import TFKerasPruningCallback
import pandas as pd
from pymongo import MongoClient
import tensorflow as tf
import fasttext
import numpy as np


language_model = fasttext.load_model("../preprocessing/lid.176.ftz")


def detect_language(text):
    pred = language_model.predict(text, k=1)
    lang = pred[0][0].replace("__label__", "")
    return lang


def parse_split(split_str):
    pieces = split_str.split(",")
    split = [float(x) for x in pieces]
    if sum(split) == 1.0 and len(split) == 3:
        return split
    else:
        raise AssertionError("Argument split is invalid")


def create_dataset(validation_split):
    num_tweets_threshold = 240
    db_name = "learning"

    client = MongoClient("localhost", 27017)
    database = client[db_name]

    sentiments = []
    labels = []

    for collection_name in database.list_collection_names():
        for document in database[collection_name].find({}):
            # get sentiments
            # data must be 3D for LSTM
            sentiment_sample = []
            for tweet in document["tweets"]:
                text = tweet["text"]
                sentiment = tweet["sentiment"]
                # check if tweet is in English
                if detect_language(text) == "en":
                    sentiment_sample.append([sentiment])
            # filter out sentiments == 0
            sentiment_sample = [x for x in sentiment_sample if x != 0]
            # filter out days with less than 100 tweets
            if len(sentiment_sample) >= num_tweets_threshold:
                sentiments.append(sentiment_sample)
                labels.append(document["price_diff"])

    sentiments = tf.ragged.constant(sentiments, inner_shape=(1,))

    labels = tf.constant(labels)

    num_data_samples = len(labels)
    split_point = int(num_data_samples * (1 - validation_split))

    training_dataset = tf.data.Dataset.from_tensor_slices(
            (sentiments[:split_point],
             labels[:split_point]))
    validation_dataset = tf.data.Dataset.from_tensor_slices(
            (sentiments[split_point:],
             labels[split_point:]))

    return training_dataset, validation_dataset


def create_dataset_twitter_three(split: list,
                                 only_nonzero: bool,
                                 tweets_threshold: int):
    client = MongoClient("localhost", 27017)
    database = client["twitter_three"]

    features_list = []
    labels_list = []

    for collection_name in database.list_collection_names():
        for document in database[collection_name].find({}):
            if not only_nonzero:
                features_list.append(document["tweets"])
                labels_list.append(document["price_diff"])
            else:  # only_nonzero
                nonzero_tweets = []
                for tweet in document["tweets"]:
                    if tweet[0] != 0:  # sentiment
                        nonzero_tweets.append(tweet)
                if len(nonzero_tweets) >= tweets_threshold:
                    features_list.append(nonzero_tweets)
                    labels_list.append(document["price_diff"])

    features = tf.ragged.constant(features_list, inner_shape=(3,))
    labels = tf.constant(labels_list)

    num_data_samples = len(labels)
    split_point_train_val = int(num_data_samples * split[0])
    split_point_val_test = int(num_data_samples * (split[0] + split[1]))

    training_dataset = tf.data.Dataset.from_tensor_slices(
            (features[:split_point_train_val],
             labels[:split_point_train_val]))
    validation_dataset = tf.data.Dataset.from_tensor_slices(
            (features[split_point_train_val:split_point_val_test],
             labels[split_point_train_val:split_point_val_test]))
    test_dataset = tf.data.Dataset.from_tensor_slices(
            (features[split_point_val_test:],
             labels[split_point_val_test:]))

    return training_dataset, validation_dataset, test_dataset


def create_model(trial):
    # Hyperparameters to be tuned by Optuna.
    learning_rate = trial.suggest_float("lr", 1e-5, 1e-3, log=True)
    units = trial.suggest_categorical("units", [16, 32, 64, 128, 256])
    rnn = trial.suggest_categorical("rnn", ["lstm", "gru"])
    loss = trial.suggest_categorical("loss", ["mse", "mae"])

    # Compose neural network with one hidden layer.
    model = tf.keras.models.Sequential()
    if rnn == "lstm":
        model.add(tf.keras.layers.LSTM(units))
    elif rnn == "gru":
        model.add(tf.keras.layers.GRU(units))
    else:
        print("Error: RNN {} not possible.".format(rnn))
    model.add(tf.keras.layers.Dense(1))

    # Compile model.
    if loss == "mse":  # mean squared error
        loss_tf = tf.keras.losses.MeanSquaredError()
    elif loss == "mae":  # mean absolute error
        loss_tf = tf.keras.losses.MeanAbsoluteError()
    else:
        print("Error: Loss {} not possible.".format(args.loss))

    model.compile(loss=loss_tf,
                  optimizer=tf.keras.optimizers.Adam(learning_rate))

    return model


def objective(trial):
    batch_size = trial.suggest_categorical("batch_size", [16, 32, 64])
    tweets_threshold = trial.suggest_categorical("tweets_threshold",
                                                 [240, 480, 720, 960])

    # Clear clutter from previous TensorFlow graphs.
    tf.keras.backend.clear_session()

    # Create tf.keras model instance.
    model = create_model(trial)

    # Create dataset instance.
    split = parse_split(args.split)
    sets = create_dataset_twitter_three(split,
                                        args.nonzero,
                                        tweets_threshold)
    train_set, val_set, test_set = sets
    train_set = train_set.shuffle(2048)
    train_set = train_set.batch(batch_size)
    val_set = val_set.batch(batch_size)
    test_set = test_set.batch(batch_size)

    # Create callbacks for early stopping and pruning.
    log_dir = "logs/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir,
                                                          profile_batch=0,
                                                          update_freq="batch")
    monitor = "val_loss"
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=3),
        TFKerasPruningCallback(trial, monitor),
        tensorboard_callback
    ]

    # Train model.
    history = model.fit(
        train_set,
        epochs=args.epochs,
        validation_data=val_set,
        callbacks=callbacks,
    )

    model.save("checkpoints/checkpoint-{}".format(trial.number))

    # Predict
    predictions = model.predict(test_set)

    # calculate R^2
    true_labels = np.concatenate([y for x, y in test_set], axis=0)
    residual_sum = np.sum(np.square(true_labels - predictions))
    true_labels_mean = np.mean(true_labels)
    total_sum = np.sum(np.square(true_labels - true_labels_mean))
    r_squared = 1 - (residual_sum / total_sum)

    # calculate mean absolute error
    mae = np.mean(np.abs(true_labels - predictions))
    # calculate mean squared error
    mse = np.mean(np.square(true_labels - predictions))

    # calculate accuracy if there would be only stock_up stock_down
    num_samples = true_labels.shape[0]
    num_correctly_classified = 0
    for true_label, prediction in zip(true_labels, predictions):
        if ((true_label > 0 and prediction > 0) or
                (true_label <= 0 and prediction <= 0)):
            num_correctly_classified = num_correctly_classified + 1
    accuracy = num_correctly_classified / num_samples

    test_stats_path = os.path.join(log_dir, "test_stats.txt")
    with open(test_stats_path, "w") as stats_file:
        stats_file.write("true labels mean: {}\n".format(true_labels_mean))
        stats_file.write("residual sum: {}\n".format(residual_sum))
        stats_file.write("total sum: {}\n".format(total_sum))
        stats_file.write("r squared: {}\n".format(r_squared))
        stats_file.write("mean absolute error: {}\n".format(mae))
        stats_file.write("mean squared error: {}\n".format(mse))
        stats_file.write("accuracy (up, down): {}\n".format(accuracy))
        stats_file.write("training history: {}\n".format(history.history))
        stats_file.write("training dataset size: {}\n".format(
            tf.data.experimental.cardinality(train_set).numpy()))
        stats_file.write("validation dataset size: {}\n".format(
            tf.data.experimental.cardinality(val_set).numpy()))
        stats_file.write("test dataset size: {}\n".format(
            tf.data.experimental.cardinality(test_set).numpy()))

    return history.history[monitor][-1]


def log_study_as_csv(study):
    data_frame = study.trials_dataframe()
    data_frame.to_csv("study.csv")


def main():
    # log arguments
    with open("study_args.txt", "w") as args_file:
        args_file.write("dataset: {}\n".format("twitter_three"))  # TODO hardcoded so far
        #  args_file.write("rnn: {}\n".format(args.rnn))
        #  args_file.write("loss: {}\n".format(args.loss))
        args_file.write("epochs: {}\n".format(args.epochs))
        args_file.write("split: {}\n".format(args.split))
        args_file.write("trials: {}\n".format(args.num_trials))
        args_file.write("nonzero: {}\n".format(args.nonzero))

    study = optuna.create_study(
        direction="minimize",
        #  pruner=optuna.pruners.MedianPruner(n_startup_trials=2)
        pruner=optuna.pruners.HyperbandPruner()
    )
    study.optimize(objective, n_trials=args.num_trials)
    log_study_as_csv(study)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training parameters")
    #  parser.add_argument("--rnn", type=str,
    #                      help="RNN layer lstm or gru")
    #  parser.add_argument("--loss", type=str,
    #                      help="Loss mse or mae")
    parser.add_argument("--epochs", type=int,
                        help="Number of epochs")
    parser.add_argument("--split", type=str,
                        help="Dataset split; train,val,test; e.g. 0.8,0.1,0,1")
    parser.add_argument("--num_trials", type=int,
                        help="Number of trials")
    parser.add_argument("--nonzero", action="store_true",
                        help="Only non-zero sentiments")
    args = parser.parse_args()

    main()
