import logging
import os
import pandas as pd
import sys
from pathlib import Path
from pymongo import MongoClient


def get(output_path: str):
    client = MongoClient()
    info_db = client["companyinfodb"]
    collection_names = info_db.list_collection_names()

    industries = set()
    sectors = set()

    for company in collection_names:
        info = info_db[company].find_one({})
        industries.add(info["Industry"])
        sectors.add(info["Sector"])

    print(industries)
    print(sectors)

    industries_list = []
    industries_values = []
    for i, industry in enumerate(industries):
        industries_list.append(industry)
        industries_values.append(float(i + 1))

    data_frame = pd.DataFrame({"industry": industries_list, "value": industries_values})
    file_name = "industries.csv"
    data_frame.to_csv(os.path.join(output_path, file_name), index=False)

    sector_list = []
    sector_values = []
    for i, sector in enumerate(sectors):
        sector_list.append(sector)
        sector_values.append(float(i + 1))

    data_frame = pd.DataFrame({"sector": sector_list, "value": sector_values})
    file_name = "sectors.csv"
    data_frame.to_csv(os.path.join(output_path, file_name), index=False)


def main():
    if sys.platform == "linux":
        base_path = os.path.join(Path.home(), "stock/stock-prediction")
    else:
        path = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        base_path = os.path.join(Path.home(), path)

    output_path = os.path.join(base_path, "preprocessing/data")
    path = "preprocessing/log/get_industry_sector.log"
    logging_path = os.path.join(base_path, path)
    logging.basicConfig(
        filename=logging_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    get(output_path)

if __name__ == "__main__":
    main()
