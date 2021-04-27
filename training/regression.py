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


def do_regression(x, y):
    # ridge regression
    reg = linear_model.Ridge()
    reg.fit(x, y)
    ridge_r2 = reg.score(x, y)

    # Bayesian regression
    reg = linear_model.BayesianRidge()
    reg.fit(x, y)
    bayesian_r2 = reg.score(x, y)

    # SVM regression
    #  for kernel in ["linear", "poly", "rbf", "sigmoid", "precomputed"]:
    reg = svm.SVR()
    reg.fit(x, y)
    svm_r2 = reg.score(x, y)

    return ridge_r2, bayesian_r2, svm_r2


def do_benchmark(data_path: str, sp500_path: str, output_path: str):
    companies = []
    sources = []
    ridge_r2 = []
    bayesian_r2 = []
    svm_r2 = []

    sp500 = read_sp500(sp500_path)
    for source in ["tweets", "ideas"]:
        for company in sp500:
            sentiment, price_diff = get_data_company(data_path,
                                                     company,
                                                     source)
            if sentiment is not None:
                ridge, bayesian, svm_r = do_regression(sentiment, price_diff)
                companies.append(company)
                sources.append(source)
                ridge_r2.append(ridge)
                bayesian_r2.append(bayesian)
                svm_r2.append(svm_r)

    for source in ["tweets", "ideas"]:
        sentiment, price_diff = get_data_set(data_path, sp500_path, source)
        ridge, bayesian, svm = do_regression(sentiment, price_diff)
        companies.append("allallall")
        sources.append(source)
        ridge_r2.append(ridge)
        bayesian_r2.append(bayesian)
        svm_r2.append(svm)

    data_frame = pd.DataFrame({"company": companies,
                               "source": sources,
                               "ridge_r2": ridge_r2,
                               "bayesian_r2": bayesian_r2,
                               "svm_r2": svm_r2})
    file_name = os.path.join(output_path, "regression.csv")
    data_frame.to_csv(file_name)


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        path = os.path.join(Path.home(),
                            "Studies/Master/10SS19/StockPrediction")
        path = os.path.join(path, "stock-prediction")
    data_path = os.path.join(path, "stats/output")
    output_path = os.path.join(path, "training/output")
    sp500_path = os.path.join(path, "crawling/data/sp500.json")

    do_benchmark(data_path, sp500_path, output_path)


if __name__ == "__main__":
    main()
