import numpy as np
import json


def main():
    files_path = "files/"
    path = path = files_path + "sp500_constituents.csv"

    sp500 = np.genfromtxt(path, dtype=None, delimiter=",", names=True, encoding="utf8")
    
    filter = sp500[:]["conm"]=="S&P 500 Comp-Ltd"
    sp500 = sp500[filter]
    filter = sp500[:]["thru"]==""
    sp500 = sp500[filter]

    sp500_dict = dict()
    sp500_dict['sp500'] = companies = sp500["co_tic"].tolist()

    with open(files_path + 'sp500.json', 'w') as json_file:
        json.dump(sp500_dict, json_file)


if __name__ == '__main__':
    main()