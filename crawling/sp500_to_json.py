import json
import numpy as np
import os


def main():
    data_path = os.path.join(".", "data")
    input_path = os.path.join(data_path, "sp500_constituents.csv")
    output_path = os.path.join(data_path, "sp500.json")

    sp500 = np.genfromtxt(input_path,
                          dtype=None,
                          delimiter=",",
                          names=True,
                          encoding="utf8")

    filtr = sp500[:]["conm"] == "S&P 500 Comp-Ltd"
    sp500 = sp500[filtr]
    filtr = sp500[:]["thru"] == ""
    sp500 = sp500[filtr]

    sp500_dict = dict()
    sp500_dict["sp500"] = sp500["co_tic"].tolist()

    with open(output_path, "w") as json_file:
        json.dump(sp500_dict, json_file, indent=4)


if __name__ == "__main__":
    main()
