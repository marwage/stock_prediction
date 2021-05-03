import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys
from pathlib import Path
from sklearn import linear_model, svm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def get_data_company(data_path: str,
                     company: str,
                     source: str):
    path = os.path.join(data_path, "sentiment_{}.csv".format(company))
    if not os.path.isfile(path):
        return None, None
    data_frame = pd.read_csv(path)
    key = "{}_sentiment_polarity_mean".format(source)
    indices = data_frame[key] != 0.0
    data_frame = data_frame[indices]
    sentiment = data_frame[key]
    price_diff = data_frame["price_diff"]
    sentiment_np = np.array(sentiment)
    price_diff_np = np.array(price_diff)

    if sentiment_np.shape[0] == 0:
        return None, None

    # satisfy scikit requirement of 2D data
    sentiment_np = sentiment_np.reshape(-1, 1)

    return sentiment_np, price_diff_np


def get_data_set(data_path: str, sp500_path: str, source: str):
    sp500 = read_sp500(sp500_path)
    sentiment = None
    price_diff = None
    for company in sp500:
        company_sentiment, company_price_diff = get_data_company(data_path,
                                                                 company,
                                                                 source)
        if sentiment is not None:
            if company_sentiment is not None:
                sentiment = np.concatenate((sentiment, company_sentiment))
                price_diff = np.concatenate((price_diff, company_price_diff))
        else:
            sentiment = company_sentiment
            price_diff = company_price_diff

    return sentiment, price_diff


def plot_regression(x: np.array,
                    y: np.array,
                    coef: np.array,
                    output_path: str,
                    source: str):
    fig, ax = plt.subplots()

    coef = float(coef)
    xy1 = (-1.0, coef * -1.0)
    xy2 = (1.0, coef)

    ax.scatter(x, y, s=1)
    ax.axline(xy1, xy2, c="red")

    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_xlabel("Mean sentiment")
    ax.set_ylabel("Relative price difference")
    ax.set_title(source.upper())

    fig.tight_layout()
    path = os.path.join(output_path, "plot_regression_{}.png".format(source))
    plt.savefig(path)


def do_regression(x, y):
    # ridge regression
    reg = linear_model.Ridge()
    reg.fit(x, y)
    return reg.coef_


def do_benchmark(data_path: str, sp500_path: str, output_path: str):
    for source in ["tweets", "ideas"]:
        sentiment, price_diff = get_data_set(data_path, sp500_path, source)
        coef = do_regression(sentiment, price_diff)
        plot_regression(sentiment, price_diff, coef, output_path, source)


def main():
    data_path = os.path.join(".", "output")
    sp500_path = os.path.join("../crawling", "data/sp500.json")

    do_benchmark(data_path, sp500_path, data_path)


if __name__ == "__main__":
    main()
