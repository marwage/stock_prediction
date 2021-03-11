import datetime
import optuna
from optuna.integration import TFKerasPruningCallback
from optuna.trial import TrialState
import pandas as pd
from pymongo import MongoClient
import tensorflow as tf
import fasttext


model = fasttext.load_model("../preprocessing/lid.176.ftz")

def detect_language(text):
    pred = model.predict(text, k=1)
    lang = pred[0][0].replace("__label__", "")
    return lang


def create_dataset(validation_split):
    num_tweets_threshold = 240
    db_name = "learning"

    client = MongoClient("localhost", 27017)
    db = client[db_name]

    sentiments = []
    labels = []

    for collection_name in db.list_collection_names():
        for document in db[collection_name].find({}):
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

    train_dataset = tf.data.Dataset.from_tensor_slices((sentiments[:split_point],
                                                        labels[:split_point]))
    val_dataset = tf.data.Dataset.from_tensor_slices((sentiments[split_point:],
                                                      labels[split_point:]))

    return train_dataset, val_dataset


def create_model(trial):
    # Hyperparameters to be tuned by Optuna.
    lr = trial.suggest_float("lr", 1e-4, 1e-2, log=True)
    units = trial.suggest_categorical("units", [128, 256, 512, 1024, 2048])

    # Compose neural network with one hidden layer.
    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(units),
        tf.keras.layers.Dense(1)
        ])

    # Compile model.
    model.compile(loss=tf.keras.losses.MeanSquaredError(),
                  optimizer=tf.keras.optimizers.Adam(lr))

    return model


def objective(trial):
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128])
    num_epochs = 1
    validation_split = 0.2

    # Clear clutter from previous TensorFlow graphs.
    tf.keras.backend.clear_session()

    # Create tf.keras model instance.
    model = create_model(trial)

    # Create dataset instance.
    train_dataset, val_dataset = create_dataset(validation_split)
    train_dataset = train_dataset.shuffle(2048)
    train_dataset = train_dataset.batch(batch_size)
    val_dataset = val_dataset.batch(batch_size)

    # Create callbacks for early stopping and pruning.
    log_dir = "logs/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
    monitor = "val_loss"
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=3),
        TFKerasPruningCallback(trial, monitor),
        tensorboard_callback
    ]

    # Train model.
    history = model.fit(
        train_dataset,
        epochs=num_epochs,
        validation_data=val_dataset,
        callbacks=callbacks,
    )
    
    model.save_weights("checkpoints/checkpoint-{}".format(trial.number))

    return history.history[monitor][-1]


def show_result(study):
    pruned_trials = study.get_trials(deepcopy=False, states=[TrialState.PRUNED])
    complete_trials = study.get_trials(deepcopy=False, states=[TrialState.COMPLETE])

    print("Study statistics: ")
    print("  Number of finished trials: ", len(study.trials))
    print("  Number of pruned trials: ", len(pruned_trials))
    print("  Number of complete trials: ", len(complete_trials))

    print("Best trial:")
    trial = study.best_trial

    print("  Value: ", trial.value)

    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))

    df = study.trials_dataframe()
    df.to_csv("optuna_study.csv")


def main():
    study = optuna.create_study(
        direction="minimize", pruner=optuna.pruners.MedianPruner(n_startup_trials=2)
    )

    study.optimize(objective, n_trials=10)

    show_result(study)


if __name__ == "__main__":
    main()
