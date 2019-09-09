import json
import requests
import random
from datetime import timedelta, datetime
from pymongo import MongoClient
from util import read_sp500
import threading
import logging


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


def divide_in_chunks(l, num):
    length = len(l)
    chunk_size = (length % num) + 1
    for i in range(0, length, chunk_size): 
        yield l[i : i+chunk_size] 


def crawl(sp500_chunk, proxies):
    client = MongoClient()
    db = client.stocktwitsdb

    all_proxies = proxies.copy()
    random.shuffle(proxies)

    timeout = 9
    proxy_index = random.randint(0, len(proxies) - 1)
    proxy = proxies[proxy_index]

    end = datetime.now() + timedelta(hours=23)
    while datetime.now() < end:
        for company in sp500_chunk:
            request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"
            successful = False
            while not successful:         
                try:
                    result = requests.get(request_url, proxies=proxy, timeout=timeout)
                    
                    if result.status_code == 200: # request was successful
                        successful = True

                        logging.debug(str(len(result.json()["messages"])) + " results for " + company)

                        # add all messages to the database
                        collection = db[company]
                        for post in result.json()["messages"]:
                            write_result = collection.update(post, post, upsert=True)
                    else: # proxy worked but API did not response as wished
                        proxy_index = random.randint(0, len(proxies) - 1)
                        proxy = proxies[proxy_index]
                except Exception as e:
                    logging.error(str(e))
                    
                    # delete the proxy that causes an exception from the list of proxies
                    del proxies[proxy_index]

                    logging.debug(str(len(proxies)) + " proxies left")

                    if len(proxies) == 0: # if all proxies are deleted
                        proxies = all_proxies.copy()
                        random.shuffle(proxies)
                    
                    # select a new proxy randomly
                    proxy_index = random.randint(0, len(proxies) - 1)
                    proxy = proxies[proxy_index]


def main():
    files_path = "/home/wagenlaeder/stock-prediction/files/"
    sp500_path = files_path + "sp500.json"
    proxy_path = files_path + "proxy_list.txt"
    log_path = files_path + "crawl_stocktwits_threading.log"

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    
    logging.info("start crawling stocktwits")

    sp500 = read_sp500(sp500_path)
    proxies = get_proxies(proxy_path)

    split_in = 10
    sp500_chunks = list(divide_in_chunks(sp500, split_in))
    proxies_chunks = list(divide_in_chunks(proxies, split_in))
    
    threads = []
    for i in range(split_in):
        thread = threading.Thread(target=crawl, args=(sp500_chunks[i], proxies_chunks[i].copy()))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    logging.info("crawling stocktwits finished")


if __name__ == '__main__':
    main()


