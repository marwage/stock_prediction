import logging
import os
import pandas as pd
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def sum_up(sp500: list, output_path: str):
    tweet_count = []
    idea_count = []
    for company in sp500:
        path = os.path.join(output_path,
                            "tweet_count_twitterdb_{}.csv".format(company))
        if os.path.isfile(path):
            data_frame = pd.read_csv(path)
            summ = data_frame["tweet_count"].sum()
            tweet_count.append(summ)
        else:
            tweet_count.append(0)

        if os.path.isfile(path):
            path = os.path.join(output_path,
                                "tweet_count_stocktwitsdb_{}.csv".format(company))
            data_frame = pd.read_csv(path)
            summ = data_frame["tweet_count"].sum()
            idea_count.append(summ)
        else:
            idea_count.append(0)

    data_frame = pd.DataFrame({"company": sp500,
                               "tweet_count": tweet_count,
                               "idea_count": idea_count})
    file_name = os.path.join(output_path, "tweet_count_company.csv")
    data_frame.to_csv(file_name)


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        path = os.path.join(Path.home(),
                            "Studies/Master/10SS19/StockPrediction")
        path = os.path.join(path, "stock-prediction")
    stats_path = os.path.join(path, "stats")
    crawling_path = os.path.join(path, "crawling")
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    log_path = os.path.join(stats_path, "log/count_tweets_company.log")
    output_path = os.path.join(stats_path, "output")

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s")

    sp500 = read_sp500(sp500_path)
    sum_up(sp500, output_path)


if __name__ == "__main__":
    main()
