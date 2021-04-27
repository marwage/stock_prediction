import os
import pandas as pd
import sys
from pathlib import Path
from sklearn import linear_model, svm


def do_regression(x, y):
    # ridge regression
    reg = linear_model.Ridge()
    reg.fit(x, y)
    r_squared = reg.score(x, y)

    print("Ridge regresion")
    print("R squared: {}".format(r_squared))
    print("---")

    # Bayesian regression
    reg = linear_model.BayesianRidge()
    reg.fit(x, y)
    r_squared = reg.score(x, y)

    print("Bayesian regression")
    print("R squared: {}".format(r_squared))
    print("---")

    # SVM regression
    reg = svm.SVR()
    reg.fit(x, y)
    r_squared = reg.score(x, y)

    print("SVM regression")
    print("R squared: {}".format(r_squared))


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        path = os.path.join(Path.home(),
                            "Studies/Master/10SS19/StockPrediction")
        path = os.path.join(path, "stock-prediction")
    data_path = os.path.join(path, "stats/output")

    path = os.path.join(data_path, "sentiment_AAPL.csv")
    data_frame = pd.read_csv(path)
    indices = data_frame["tweets_sentiment_polarity_mean"] != 0.0
    data_frame = data_frame[indices]
    sentiment = data_frame["tweets_sentiment_polarity_mean"]
    sentiment = sentiment.to_numpy()
    price_diff = data_frame["price_diff"]
    price_diff = price_diff.to_numpy()

    # satisfy scikit requirement of 2D data
    sentiment = sentiment.reshape(-1, 1)

    do_regression(sentiment, price_diff)


if __name__ == "__main__":
    main()
