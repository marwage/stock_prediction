import json
import requests
import random
from datetime import timedelta, datetime
from pymongo import MongoClient


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def get_proxies(path):
    proxies = []

    with open(path, "r") as proxy_file:
        proxy_lines = proxy_file.readlines()

    for row in proxy_lines:
        row = row.replace("\n", "")
        proxy = dict()
        proxy["https"] = "http://" + row
        proxies.append(proxy)
        
    return proxies


def query_store(sp500, proxies):    
    client = MongoClient()
    db = client.stocktwitsdb

    for company in sp500:
        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"

        successful = False
        while not successful:
            proxy_index = random.randint(0, len(proxies) - 1)
            proxy = proxies[proxy_index]
            
            result = requests.get(request_url, proxies=proxy)        
            write_to_log(str(result))

            if result.status_code == 200:
                successful = True


def write_to_log(text):
    log_path = "files/crawl_stocktwits_2-3.log"
    
    with open(log_path, "a") as log:
        log.write(text + "\n")

    return


def main():
    sp500_path = "files/sp500.json"
    proxy_path = "files/proxy_list.txt"

    write_to_log(str(datetime.now()) + " started")

    sp500 = read_sp500(sp500_path)
    proxies = get_proxies(proxy_path)
    query_store(sp500, proxies)

    write_to_log(str(datetime.now()) + " finished")


if __name__ == '__main__':
    main()


