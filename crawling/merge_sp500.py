import json
import os
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def merge(a, b):
    sp500_dict = dict()
    set_a = set(a)
    set_b = set(b)
    union = set_a.union(set_b)
    sp500_dict["sp500"] = list(union)
    return sp500_dict

def main():
    sp500_path = os.path.join(".", "data/sp500_20190918.json")
    sp500_a = read_sp500(sp500_path)
    sp500_path = os.path.join(".", "data/sp500_20210125.json")
    sp500_b = read_sp500(sp500_path)

    sp500 = merge(sp500_a, sp500_b)

    sp500_path = os.path.join(".", "data/sp500.json")
    with open(sp500_path, "w") as sp500_file:
        json.dump(sp500, sp500_file)


if __name__ == "__main__":
    main()
