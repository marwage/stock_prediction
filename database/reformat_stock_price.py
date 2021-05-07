import json
import os
from datetime import datetime
from pymongo import MongoClient


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def reformat_stock_price(sp500):
    client = MongoClient()
    db = client.stockpricedb

    for company in sp500:
        company_coll = db[company]
        days = company_coll.find()
        for day in days:
            keys = day.keys()
            if "date" not in keys:  # not updated
                for key in keys:
                    if key != "_id":  # key with date
                        attr = day[key]
                        date = datetime.strptime(key, "%Y-%m-%d")
                        day_properties = dict()
                        day_properties["date"] = date
                        day_properties["open"] = attr["open"]
                        day_properties["high"] = attr["high"]
                        day_properties["low"] = attr["low"]
                        day_properties["close"] = attr["close"]
                        day_properties["volume"] = attr["volume"]

                        company_coll.replace_one({"_id": day["_id"]},
                                                 day_properties,
                                                 upsert=True)

def main():
    sp500_path = os.path.join("../crawling", "data/sp500.json")

    sp500 = read_sp500(sp500_path)
    reformat_stock_price(sp500)


if __name__ == "__main__":
    main()
