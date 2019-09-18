import numpy as np
import json


def main():
    data_path = "stock-prediction/crawling/data"
    input_path = data_path + "sp500_constituents.csv"
    output_path = data_path + "sp500.json"

    sp500 = np.genfromtxt(input_path, dtype=None, delimiter=",", names=True, encoding="utf8")
    
    filter = sp500[:]["conm"]=="S&P 500 Comp-Ltd"
    sp500 = sp500[filter]
    filter = sp500[:]["thru"]==""
    sp500 = sp500[filter]

    sp500_dict = dict()
    sp500_dict["sp500"] = sp500["co_tic"].tolist()

    with open(output_path, "w") as json_file:
        json.dump(sp500_dict, json_file)


if __name__ == "__main__":
    main()