import numpy as np


def read_sp500():
	sp500_path = "files/sp500_constituents.csv"

	sp500 = np.genfromtxt(sp500_path, dtype=None, delimiter=",", names=True, encoding="utf8")
	filter = sp500[:]["conm"]=="S&P 500 Comp-Ltd"
	sp500 = sp500[filter]
	filter = sp500[:]["thru"]==""
	sp500 = sp500[filter]
	
	return sp500


def main():
    sp500 = read_sp500()


if __name__ == '__main__':
    main()