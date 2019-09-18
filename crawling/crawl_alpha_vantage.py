import requests
import json
from pymongo import MongoClient
from datetime import datetime
import time
import random
import logging
from read_sp500 import read_sp500


def get_apikey(path):
    with open(path, "r") as json_file:
        apikey_json = json.load(json_file)

    return apikey_json["apikey"]


def query_stock_price(apikey, sp500):
    client = MongoClient()
    db = client.stockpricedb

    for company in sp500:
        sucessful = False
        while not sucessful:
            request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + company + "&interval=5min&apikey=" + apikey
            result = requests.get(request_url)
            if result.status_code == 200:
                try:
                    items = result.json()["Time Series (Daily)"].items()
                    sucessful = True
                except Exception as e:
                    logging.error(str(e))
                    time.sleep(60)
                    break

                collection = db[company]
                for key, value in result.json()["Time Series (Daily)"].items():
                    date = datetime.strptime(key, "%Y-%m-%d")
                    if date > datetime(2019, 6, 1):
                        entry = dict()
                        entry[key] = dict()
                        entry[key]["open"] = float(value["1. open"])
                        entry[key]["high"] = float(value["2. high"])
                        entry[key]["low"] = float(value["3. low"])
                        entry[key]["close"] = float(value["4. close"])
                        entry[key]["volume"] = float(value["5. volume"])
                        
                        write_result = collection.update(entry, entry, upsert=True)
            else:
                logging.debug(str(result))


def main():
    crawling_path = "stock-prediction/crawling/"
    sp500_path = crawling_path + "data/sp500.json"
    apikey_path = crawling_path + "access-token/alpha-vantage-apikey.json"
    log_path = crawling_path + "log/crawl-alpha-vantage.log"

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    apikey = get_apikey(apikey_path)
    sp500 = read_sp500(sp500_path)
    random.shuffle(sp500)
    stock_price = query_stock_price(apikey, sp500)


if __name__ == '__main__':
    main()

