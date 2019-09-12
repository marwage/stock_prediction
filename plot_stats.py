import json
import matplotlib.pyplot as plt
import numpy as np
from pymongo import MongoClient
from datetime import datetime


def plot_stats():
    files_path = "files/"
    stats_path = files_path + "stocktwits_stats.json"
    sp500_path = files_path + "sp500.json"
    save_path = files_path + "graphs/stocktwits/"

    # mongodb
    client = MongoClient()
    db = client.stocktwitsdb

    for share_code in db.list_collection_names():
        collection = db[share_code]
        stats = dict()
        for post in collection.find({}):
            date_string = post['created_at']
            post_date = datetime.strptime(date_string[0:10], '%Y-%m-%d')
            date_string = post_date.strftime('%Y-%m-%d')
            if date_string in stats:
                stats[date_string] = stats[share_code][date_string] + 1
            else:
                stats[date_string] = 1

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
        ax.tick_params(axis="y", labelsize=4)

        p1 = plt.barh(ind, counts, height)

        plt.xlabel("Counts")
        plt.title(share_code + " messages per day")
        plt.yticks(ind, dates)

        plt.savefig(save_path + share_code + ".svg")
        plt.close()


if __name__ == '__main__':
    plot_stats()
