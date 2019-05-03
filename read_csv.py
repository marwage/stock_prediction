import numpy as np


def main():
	sp500_path = "/Volumes/NiftySwifty/StockData/sp500_constituents.csv"

	companies = np.genfromtxt(sp500_path, dtype=None, delimiter=",", names=True, encoding="utf8")

	filter = companies[:]["conm"]=="S&P 500 Comp-Ltd"
	sp500 = companies[filter]

	filter = sp500[:]["thru"]==""
	current_sp500 = sp500[filter]
	
	current_sp500_na = current_sp500[:][["co_conm", "co_tic"]]

	np.savetxt("tmp/current_sp500.csv", current_sp500_na, fmt="%s", delimiter=",")


if __name__ == "__main__":
	main()


# co_tic are the stock abbreviations