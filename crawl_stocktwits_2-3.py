import json
import requests
import random
from datetime import timedelta, datetime
from pymongo import MongoClient


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def get_proxies(paths):
    proxies = []

    for path in paths:
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

    timeout = 6
    proxy_index = random.randint(0, len(proxies) - 1)
    proxy = proxies[proxy_index]

    for company in sp500:
        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"

        successful = False
        while not successful:         
            try:
                result = requests.get(request_url, proxies=proxy, timeout=timeout)
                
                
                if result.status_code == 200:
                    successful = True
                    write_to_log(str(len(result.json()["messages"])) + " results for " + company)

                    collection = db[company]
                    for post in result.json()["messages"]:
                        write_result = collection.update(post, post, upsert=True)
                else:
                    proxy_index = random.randint(0, len(proxies) - 1)
                    proxy = proxies[proxy_index]
            except Exception as e:
                write_to_log(str(e))
                del proxies[proxy_index]
                write_to_log("proxy " + proxy["https"] + " deleted")
                proxy_index = random.randint(0, len(proxies) - 1)
                proxy = proxies[proxy_index]


def write_to_log(text):
    log_path = "files/crawl_stocktwits_2-3.log"
    
    with open(log_path, "a") as log:
        log.write(str(datetime.now()) + " " + text.replace("\n", " ") + "\n")

    return


def main():
    sp500_path = "files/sp500.json"
    proxy_paths = ["files/proxy_list.txt", "files/proxy_list_2.txt"]

    write_to_log("start crawling stocktwits")

    sp500 = read_sp500(sp500_path)
    proxies = get_proxies(proxy_paths)
    query_store(sp500, proxies)

    write_to_log("crawling stocktwits finished")


if __name__ == '__main__':
    main()


