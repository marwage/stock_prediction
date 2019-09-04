import json
import sys
from datetime import timedelta, datetime
import time
from pymongo import MongoClient

from urllib.request import Request, urlopen
from fake_useragent import UserAgent
import random


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def query_store(sp500):
    start_time = datetime.now()
    client = MongoClient()
    db = client.stocktwitsdb
    user_agent = UserAgent()
    proxy = "35.231.212.6:443"

    for company in sp500:

        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"
        req = Request(request_url)
        req.add_header('User-Agent', user_agent.random)
        req.set_proxy(proxy, "https")

        try:
            result = urlopen(req).read().decode('utf8')
            print(type(result))
            sys.exit()
        except Exception as e:
            write_to_log(str(e))


def write_to_log(text):
    log_path = "files/crawl_stocktwits_2.log"
    
    with open(log_path, "a") as log:
        log.write(text + "\n")

    return


def main():
    sp500_path = "files/sp500.json"
    proxy_path = "files/proxy_list_2.txt"

    sp500 = read_sp500(sp500_path)
    query_store(sp500)

    write_to_log(str(datetime.now()) + " finished")


if __name__ == '__main__':
    main()


