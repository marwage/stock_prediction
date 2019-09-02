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

    ind = np.arange(n) 
    width = 0.3

    p1 = plt.bar(ind, counts, width)

    plt.ylabel('Counts')
    plt.title('AAPL counts per day')
    plt.xticks(ind, dates, rotation='vertical')

    plt.savefig('stocktwits_AAPL.svg')


if __name__ == '__main__':
    main()
