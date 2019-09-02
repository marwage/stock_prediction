import json
import matplotlib.pyplot as plt
import numpy as np


def main():
    with open('stocktwits_stats.json', 'r') as json_file:
        stats = json.load(json_file)

    apple = stats['AAPL']
    n = 0
    dates = []
    counts = []
    for key, value in apple.items():
        dates.append(key)
        counts.append(value)
        n = n + 1

    ind = np.arange(n) * 1
    height = 0.5

    fig, ax = plt.subplots()
    ax.tick_params(axis='y', labelsize=4)

    p1 = plt.barh(ind, counts, height)

    plt.xlabel('Counts')
    plt.title('AAPL counts per day')
    plt.yticks(ind, dates)

    plt.savefig('stocktwits_AAPL.svg')


if __name__ == '__main__':
    main()
