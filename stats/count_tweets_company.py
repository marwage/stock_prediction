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
    sp500_path = os.path.join("../crawling", "data/sp500.json")
    log_path = os.path.join(".", "log/count_tweets_company.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s")

    sp500 = read_sp500(sp500_path)
    sum_up(sp500, output_path)


if __name__ == "__main__":
    main()
