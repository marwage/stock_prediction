import json
import numpy as np
import os
import pandas as pd
import scipy
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


def get_p_values(reg, x, y):
    params = np.append(reg.intercept_, reg.coef_)
    predictions = reg.predict(x)

    new_x = np.append(np.ones((len(x), 1)), x, axis=1)
    mse = (sum((y-predictions)**2))/(len(new_x)-len(new_x[0]))

    var_b = mse*(np.linalg.inv(np.dot(new_x.T, new_x)).diagonal())
    sd_b = np.sqrt(var_b)
    ts_b = params / sd_b

    p_values = [2*(1-scipy.stats.t.cdf(np.abs(i), (len(new_x)-len(new_x[0])))) for i in ts_b]

    stats = dict()
    stats["intercept"] = {"coefficient": params[0],
                          "standard_error": sd_b[0],
                          "t_value": ts_b[0],
                          "p_value": p_values[0]}
    stats["coefficients"] = []
    for i in range(1, params.shape[0]):
        stats["coefficients"].append({"coefficient": params[i],
                                      "standard_error": sd_b[i],
                                      "t_value": ts_b[i],
                                      "p_value": p_values[i]})

    return stats


def do_ridge_regression(x, y):
    reg = linear_model.Ridge()
    reg.fit(x, y)
    ridge_r2 = reg.score(x, y)

    return reg, ridge_r2


def do_bayesian_regression(x, y):
    reg = linear_model.BayesianRidge()
    reg.fit(x, y)
    bayesian_r2 = reg.score(x, y)

    return reg, bayesian_r2


def do_svm_regression(x, y):
    for kernel in ["linear", "poly", "rbf", "sigmoid", "precomputed"]:
        reg = svm.SVR()
        reg.fit(x, y)
        svm_r2 = reg.score(x, y)
        print("kernel {}".format(kernel))
        print("r2 {}".format(svm_r2))

    return reg, svm_r2


def do_benchmark(data_path: str, sp500_path: str, output_path: str):
    regression = dict()

    sp500 = read_sp500(sp500_path)
    for company in sp500:
        regression[company] = dict()
        for source in ["tweets", "ideas"]:
            sentiment, price_diff = get_data_company(data_path,
                                                     company,
                                                     source)
            if sentiment is not None:
                reg, ridge_r2 = do_ridge_regression(sentiment, price_diff)
                ridge_stats = get_p_values(reg, sentiment, price_diff)
                ridge_stats["r_squared"] = ridge_r2
                reg, bayesian_r2 = do_bayesian_regression(sentiment, price_diff)
                bayesian_stats = get_p_values(reg, sentiment, price_diff)
                bayesian_stats["r_squared"] = bayesian_r2
                reg, svm_r2 = do_svm_regression(sentiment, price_diff)
                svm_stats = {"r_squared": svm_r2}
                stats = {"ridge": ridge_stats,
                         "bayesian_ridge": bayesian_stats,
                         "svm": svm_stats}
                regression[company][source] = stats

    company = "allallall"
    regression[company] = dict()
    for source in ["tweets", "ideas"]:
        sentiment, price_diff = get_data_set(data_path,
                                             sp500_path,
                                             source)
        reg, ridge_r2 = do_ridge_regression(sentiment, price_diff)
        ridge_stats = get_p_values(reg, sentiment, price_diff)
        ridge_stats["r_squared"] = ridge_r2
        reg, bayesian_r2 = do_bayesian_regression(sentiment, price_diff)
        bayesian_stats = get_p_values(reg, sentiment, price_diff)
        bayesian_stats["r_squared"] = bayesian_r2
        reg, svm_r2 = do_svm_regression(sentiment, price_diff)
        svm_stats = {"r_squared": svm_r2}
        stats = {"ridge": ridge_stats,
                 "bayesian_ridge": bayesian_stats,
                 "svm": svm_stats}
        regression[company][source] = stats

    file_name = os.path.join(output_path, "regression.json")
    with open(file_name, "w") as json_file:
        json.dump(regression, json_file, indent=4)


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
