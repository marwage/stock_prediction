import json
import matplotlib.pyplot as plt
import numpy as np
from util import read_sp500


def main():
    files_path = "files/"
    stats_path = files_path + "stocktwits_stats.json"
    sp500_path = files_path + "sp500.json"
    save_path = files_path + "graphs/stocktwits/"

    sp500 = read_sp500(sp500_path)

    with open(stats_path, "r") as json_file:
        stats = json.load(json_file)

    for company in sp500:
        company_stats = stats[company]
        n = 0
        dates = []
        counts = []
        for key, value in company_stats.items():
            dates.append(key)
            counts.append(value)
            n = n + 1

        ind = np.arange(n) * 1
        height = 0.5

        fig, ax = plt.subplots()
        ax.tick_params(axis="y", labelsize=4)

        p1 = plt.barh(ind, counts, height)

        plt.xlabel("Counts")
        plt.title(company + " messages per day")
        plt.yticks(ind, dates)

        plt.savefig(save_path + company + ".svg")


if __name__ == '__main__':
    main()
