import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from pathlib import Path
import math


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]

def set_stock_price_diff(sp500):
    client = MongoClient()
    stockprice_db = client["stockpricedb"]
    learning_db = client["learning"]

    for company in sp500:
        print(company)

        company_stockprice = stockprice_db[company]
        company_learning = learning_db[company]

        num_nones = 0
        days = company_learning.find()
        for day in days:
            date = day["day"]
            day_prop = company_stockprice.find_one({"date": date})
            
            next_day = date + timedelta(days=1)
            next_day_prop = company_stockprice.find_one({"date": next_day})
            if day_prop is None or next_day_prop is None:
                update_result = company_learning.update_one({"_id": day["_id"]}, {"$set": {"price_diff": math.nan}})
                num_nones = num_nones + 1
            else:
                stock_price_day = day_prop["open"]
                stock_price_next_day = next_day_prop["open"]
                diff = stock_price_next_day - stock_price_day

                company_learning.update_one({"_id": day["_id"]}, {"$set": {"price_diff": diff}})
                

        print("Number of Nones is {}".format(num_nones))

def main():
    sp500_path = os.path.join(Path.home(),
            "Studies/Master/10SS19/StockPrediction/stock-prediction/crawling/data/sp500.json")

    sp500 = read_sp500(sp500_path)
    set_stock_price_diff(sp500)


if __name__ == '__main__':
    main()
