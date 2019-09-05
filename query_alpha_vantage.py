import requests
import json
from pymongo import MongoClient
from datetime import datetime


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def get_apikey(path):
    with open(path, "r") as json_file:
        apikey_json = json.load(json_file)

    return apikey_json["apikey"]


def write_to_log(text):
    log_path = "/home/wagenlaeder/stock-prediction/files/crawl_stocktwits2.log"
    
    with open(log_path, "a") as log:
        log.write(str(datetime.now()) + " " + text.replace("\n", " ") + "\n")

    return


def query_stock_price(apikey, sp500):
    client = MongoClient()
    db = client.stockpricedb

    for company in sp500:
        request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + company + "&interval=5min&apikey=" + apikey
        result = requests.get(request_url)
        if result.status_code == 200:
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
            write_to_log("error " + result.status_code)


def main():
    files_path = "/home/wagenlaeder/stock-prediction/files/"
    sp500_path = files_path + "sp500.json"
    apikey_path = files_path + "alpha_vantage_apikey.json"
    apikey = get_apikey(apikey_path)
    sp500 = read_sp500(sp500_path)
    stock_price = query_stock_price(apikey, sp500)


if __name__ == '__main__':
    main()

