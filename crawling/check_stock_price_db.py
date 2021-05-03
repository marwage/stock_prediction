import datetime
import logging
import os
import pandas as pd
import sys
from pathlib import Path
from pymongo import MongoClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.read_sp500 import read_sp500


def check(sp500: list, output_path: str):
    client = MongoClient()
    stockprice_db = client["stockpricedb"]

    for company in sp500:
        collection = stockprice_db[company]

        days = []
        has_entry = []

        start_day = datetime.datetime(2019, 4, 1)
        end_day = datetime.datetime.now()
        current_day = start_day

        while current_day < end_day:
            logging.debug("Check %s on %s", company, current_day)
            found_days = collection.count_documents({"date": current_day})
            if found_days == 0:
                days.append(current_day)
                has_entry.append(False)
            elif found_days == 1:
                days.append(current_day)
                has_entry.append(True)
            else:  # should not be the case
                logging.error("Database has duplicates")

            current_day = current_day + datetime.timedelta(days=1)

        data_frame = pd.DataFrame({"day": days, "has_entry": has_entry})
        file_name = "stock_price_availability_{}.csv".format(company)
        data_frame.to_csv(os.path.join(output_path, file_name))


def main():
    sp500_path = os.path.join(".", "data/sp500.json")
    log_path = os.path.join(".", "log/check_stock_price_db.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    check(sp500, output_path)


if __name__ == "__main__":
    main()
