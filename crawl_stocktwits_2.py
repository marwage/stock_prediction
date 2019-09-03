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


def get_proxies(path):
    proxies = []

    with open(path, "r") as proxy_file:
        proxy_lines = proxy_file.readlines()

    for row in proxy_lines:
        row = row.replace("\n", "")
        row_split = row.split(":")
        proxy = dict()
        proxy["ip"] = row_split[0]
        proxy["port"] = row_split[1]
        proxies.append(proxy)
        
    return proxies


def query_store(sp500, proxies):
    start_time = datetime.now()
    client = MongoClient()
    db = client.stocktwitsdb
    user_agent = UserAgent()

    for company in sp500:
        # pick random proxy
        proxy_index = random.randint(0, len(proxies) - 1)
        proxy = proxies[proxy_index]

        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"
        req = Request(request_url)
        req.add_header('User-Agent', user_agent.random)
        req.set_proxy(proxy["ip"] + ":" + proxy["port"], "https")

        successful = False
        while not successful:
            try:
                result = urlopen(req).read().decode('utf8')
                print(type(result))
                successful = True
            except Exception as e:
                write_to_log(str(e))
                del proxies[proxy_index]
                write_to_log("proxy " + proxy["ip"] + ":" + proxy["port"] + " deleted")
                if len(proxies) == 0:
                    write_to_log("no proxies left")
                    sys.exit()
                else:
                    proxy_index = random.randint(0, len(proxies) - 1)
                    proxy = proxies[proxy_index]

        # write_to_log(str(datetime.now()) + " " + str(len(result.json()["messages"])) + " results for " + company)

        #collection = db[company]
        #for post in result.json()["messages"]:
        #    write_result = collection.update(post, post, upsert=True)


def write_to_log(text):
    log_path = "files/crawl_stocktwits_2.log"
    
    with open(log_path, "a") as log:
        log.write(text + "\n")

    return


def main():
    sp500_path = "files/sp500.json"
    proxy_path = "files/proxy_list.txt"

    sp500 = read_sp500(sp500_path)
    proxies = get_proxies(proxy_path)
    query_store(sp500, proxies)

    write_to_log(str(datetime.now()) + " finished")


if __name__ == '__main__':
    main()


