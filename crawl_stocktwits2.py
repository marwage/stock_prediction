import json
import requests
import random
from datetime import timedelta, datetime
from pymongo import MongoClient
from util import read_sp500, write_to_log


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


def crawl(sp500, proxies):
    log_path = "/home/wagenlaeder/stock-prediction/files/crawl_stocktwits2.log"

    client = MongoClient()
    db = client.stocktwitsdb

    timeout = 9
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
                    write_to_log(log_path, str(len(result.json()["messages"])) + " results for " + company)

                    collection = db[company]
                    for post in result.json()["messages"]:
                        query = {
                            "body": post["body"],
                            "created_at": post["created_at"]
                            }
                        write_result = collection.update(post, post, upsert=True)
                else:
                    proxy_index = random.randint(0, len(proxies) - 1)
                    proxy = proxies[proxy_index]
            except Exception as e:
                write_to_log(log_path, str(e))
                del proxies[proxy_index]
                write_to_log(log_path, "proxy " + proxy["https"] + " deleted")
                write_to_log(log_path, str(len(proxies)) + " proxies left")
                proxy_index = random.randint(0, len(proxies) - 1)
                proxy = proxies[proxy_index]


def main():
    files_path = "/home/wagenlaeder/stock-prediction/files/"
    sp500_path = files_path + "sp500.json"
    proxy_path = files_path + "proxy_list.txt"
    log_path = files_path + "crawl_stocktwits2.log"

    write_to_log(log_path, "start crawling stocktwits")

    sp500 = read_sp500(sp500_path)
    proxies = get_proxies(proxy_path)

    end = datetime.now() + timedelta(hours=23)

    while datetime.now() < end:
        crawl(sp500, proxies)

    write_to_log(log_path, "crawling stocktwits finished")


if __name__ == '__main__':
    main()


