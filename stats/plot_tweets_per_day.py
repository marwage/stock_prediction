import json
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
from pymongo import MongoClient
from datetime import datetime


def plot_company_stats(db_name, company, stats, output_path):
    logging.info("plot stats of " + company)

    n = 0
    dates = []
    counts = []
    for key, value in stats.items():
        dates.append(key)
        counts.append(value)
        n = n + 1

    ind = np.arange(n) * 1
    height = 0.5

    fig, ax = plt.subplots()

    plt.rcParams['figure.figsize'] = [8, 32]
    plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
    plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True

    ax.tick_params(axis="y", labelsize=10)
    ax.xaxis.set_label_position("top")
    ax.xaxis.grid(True)

    plt.barh(ind, counts, height)

    plt.xlabel("Number of messages")
    plt.title(company + " messages per day")
    plt.yticks(ind, dates)

    file_name = os.path.join(output_path,
                             "plot_stats_{}_{}.svg".format(db_name, company))
    plt.savefig(file_name)
    plt.close()


def plot_stats(db_name: str, output_path: str):
    client = MongoClient()
    db = client[db_name]

    for company in db.list_collection_names():
        logging.debug("get posts of " + company)
        collection = db[company]
        company_stats = dict()
        for post in collection.find({}):
            date_string = post["created_at"]
            if db_name == "stocktwitsdb":
                post_date = datetime.strptime(date_string[0:10], "%Y-%m-%d")
            elif db_name == "twitterdb":
                post_date = datetime.strptime(date_string,
                                              "%a %b %d %H:%M:%S %z %Y")
            else:
                logging.error("database not found")
            date_string = post_date.strftime('%Y-%m-%d')
            if date_string in company_stats:
                company_stats[date_string] = company_stats[date_string] + 1
            else:
                company_stats[date_string] = 1
        plot_company_stats(db_name, company, company_stats, output_path)


def main():
    log_path = os.path.join(".", "log/plot_stats.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    plot_stats("stocktwitsdb", output_path)
    plot_stats("twitterdb", output_path)


if __name__ == "__main__":
    main()
