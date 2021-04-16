import json
import logging
import os
import requests
import random
import threading
from datetime import timedelta, datetime
from pathlib import Path
from pymongo import MongoClient
from read_sp500 import read_sp500


def get_working_proxies(path):
    with open(path, "r") as proxy_file:
        proxies = json.load(proxy_file)

    return proxies


def divide_in_chunks(lis, num):
    length = len(lis)
    chunk_size = (length // num)
    for i in range(0, length, chunk_size):
        yield lis[i: i+chunk_size]


def crawl(sp500_chunk, proxies):
    client = MongoClient()
    database = client.stocktwitsdb

    all_proxies = proxies.copy()
    random.shuffle(proxies)

    timeout = 15
    proxy_index = random.randint(0, len(proxies) - 1)
    proxy = proxies[proxy_index]

    while True:
        for company in sp500_chunk:
            request_url = "https://api.stocktwits.com/api/2/streams/symbol/" \
                + company + ".json"
            successful = False
            while not successful:
                try:
                    result = requests.get(request_url,
                                          proxies=proxy,
                                          timeout=timeout)

                    if result.status_code == 200:  # request was successful
                        successful = True
                        result_json = result.json()

                        logging.info("%d results for %s",
                                     len(result_json),
                                     company)

                        # add all messages to the database
                        collection = database[company]
                        for post in result.json()["messages"]:
                            query = {
                                "body": post["body"],
                                "created_at": post["created_at"]
                                }
                            collection.update_one(query, post, upsert=True)
                    else:  # proxy worked but API did not response as wished
                        proxy_index = random.randint(0, len(proxies) - 1)
                        proxy = proxies[proxy_index]
                except Exception as e:
                    logging.debug(str(e))

                    # delete the proxy that causes an exception from the list
                    del proxies[proxy_index]

                    logging.debug("%d proxies left", len(proxies))

                    if len(proxies) == 0:  # if all proxies are deleted
                        proxies = all_proxies.copy()
                        random.shuffle(proxies)

                    # select a new proxy randomly
                    proxy_index = random.randint(0, len(proxies) - 1)
                    proxy = proxies[proxy_index]


def main():
    crawling_path = os.path.join(Path.home(), "stock-prediction/crawling")
    sp500_path = os.path.join(crawling_path, "data/sp500.json")
    proxy_path = os.path.join(crawling_path, "data/working_proxies.json")
    log_path = os.path.join(crawling_path, "log/stocktwits.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    sp500 = read_sp500(sp500_path)
    proxies = get_working_proxies(proxy_path)

    num_threads = 24
    sp500_chunks = list(divide_in_chunks(sp500, num_threads))
    proxies_chunks = list(divide_in_chunks(proxies, num_threads))

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=crawl,
                                  args=(sp500_chunks[i],
                                        proxies_chunks[i].copy()))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()