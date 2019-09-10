import json
import requests
import random
from datetime import timedelta, datetime
from pymongo import MongoClient
from util import read_sp500
import threading
import logging


def get_working_proxies(path):
    with open(path, "r") as proxy_file:
        proxies = json.load(proxy_file)

    return proxies


def divide_in_chunks(lis, num):
    length = len(lis)
    chunk_size = (length // num) + 1
    for i in range(0, length, chunk_size): 
        yield lis[i : i+chunk_size] 


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
    proxy_path = files_path + "working_proxies.json"
    log_path = files_path + "crawl_stocktwits_threading.log"

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    
    logging.info("start crawling stocktwits")

    sp500 = read_sp500(sp500_path)
    proxies = get_working_proxies(proxy_path)
    
    num_threads = 24
    sp500_chunks = list(divide_in_chunks(sp500, num_threads))
    proxies_chunks = list(divide_in_chunks(proxies, num_threads))
    
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=crawl, args=(sp500_chunks[i], proxies_chunks[i].copy()))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    logging.info("crawling stocktwits finished")


if __name__ == '__main__':
    main()


