import datetime
import optuna
from optuna.integration import TFKerasPruningCallback
from optuna.trial import TrialState
import pandas as pd
from pymongo import MongoClient
import tensorflow as tf
import fasttext
import argparse
import os
import numpy as np


model = fasttext.load_model("../preprocessing/lid.176.ftz")

def detect_language(text):
    pred = model.predict(text, k=1)
    lang = pred[0][0].replace("__label__", "")
    return lang

def parse_split(split_str):
    pieces = split_str.split(",")
    split = [float(x) for x in pieces]
    if sum(split) != 1.0 or len(split) != 3:
        raise Error("Argument split is invalid")
    else:
        return split


def create_dataset_twitter_three(split):
    db_name = "twitter_three"

    client = MongoClient("localhost", 27017)
    db = client[db_name]

    features_list = []
    labels_list = []

    for collection_name in db.list_collection_names():
        for document in db[collection_name].find({}):
            features_list.append(document["tweets"])
            labels_list.append(document["price_diff"])

    features = tf.ragged.constant(features_list, inner_shape=(3,))

    labels_class_list = [0 if price > 0 else 1 for price in labels_list]

    labels = tf.constant(labels_class_list)

    num_data_samples = len(labels)
    split_point_train_val = int(num_data_samples * split[0])
    split_point_val_test = int(num_data_samples * (split[0] + split[1]))

    train_dataset = tf.data.Dataset.from_tensor_slices((features[:split_point_train_val],
                                                        labels[:split_point_train_val]))
    val_dataset = tf.data.Dataset.from_tensor_slices(
            (features[split_point_train_val:split_point_val_test],
            labels[split_point_train_val:split_point_val_test]))
    test_dataset = tf.data.Dataset.from_tensor_slices(
            (features[split_point_val_test:],
            labels[split_point_val_test:]))

    return train_dataset, val_dataset, test_dataset


def create_model(trial):
    # Hyperparameters to be tuned by Optuna.
    lr = trial.suggest_float("lr", 1e-4, 1e-2, log=True)
    units = trial.suggest_categorical("units", [8, 16, 32, 64, 128, 256, 512])

    # Compose neural network with one hidden layer.
    model = tf.keras.models.Sequential()
    if args.rnn == "lstm":
        model.add(tf.keras.layers.LSTM(units))
    elif args.rnn =="gru":
        model.add(tf.keras.layers.GRU(units))
    else:
        print("Error: RNN {} not possible.".format(rnn))
    model.add(tf.keras.layers.Dense(1))
    model.add(tf.keras.layers.Softmax())

    # Compile model.
    loss = tf.keras.losses.BinaryCrossentropy()

    model.compile(loss=loss,
                  optimizer=tf.keras.optimizers.Adam(lr))

    return model


def objective(trial):
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32, 64, 128])

    # Clear clutter from previous TensorFlow graphs.
    tf.keras.backend.clear_session()

    # Create tf.keras model instance.
    model = create_model(trial)

    # Create dataset instance.
    #  train_dataset, val_dataset = create_dataset(validation_split)
    split = parse_split(args.split)
    train_set, val_set, test_set = create_dataset_twitter_three(split)
    train_set = train_set.shuffle(2048)
    train_set = train_set.batch(batch_size)
    val_set = val_set.batch(batch_size)
    test_set = test_set.batch(batch_size)

    # Create callbacks for early stopping and pruning.
    log_dir = "logs/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, update_freq="batch")
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

    # Accuracy
    true_labels = np.concatenate([y for x, y in test_set], axis=0)
    m = tf.keras.metrics.Accuracy()
    m.update_state(true_labels, predictions)
    accuracy = m.result().numpy()


    test_stats_path = os.path.join(log_dir, "test_stats.txt")
    with open(test_stats_path, "w") as stats_file:
        stats_file.write("accuracy: {}\n".format(accuracy))

    return history.history[monitor][-1]


def log_study_as_csv(study):
    df = study.trials_dataframe()
    df.to_csv("optuna_study.csv")


def main():
    # log arguments
    with open("study_args.txt", "w") as args_file:
        args_file.write("dataset: {}\n".format("twitter_three")) # TODO hardcoded so far
        args_file.write("rnn: {}\n".format(args.rnn))
        args_file.write("epochs: {}\n".format(args.epochs))
        args_file.write("split: {}\n".format(args.split))
        args_file.write("trials: {}\n".format(args.num_trials))


    # study
    study = optuna.create_study(
        direction="minimize", pruner=optuna.pruners.MedianPruner(n_startup_trials=2)
    )
    study.optimize(objective, n_trials=args.num_trials)
    log_study_as_csv(study)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training parameters")
    parser.add_argument("--rnn", type=str,
                        help="RNN layer lstm or gru")
    parser.add_argument("--epochs", type=int,
                        help="Number of epochs")
    parser.add_argument("--split", type=str,
                        help="Dataset split; training, validation, test; e.g. 0.8,0.1,0,1")
    parser.add_argument("--num_trials", type=int,
                        help="Number of trials")
    args = parser.parse_args()

    main()
