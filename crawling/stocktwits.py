import datetime
import json
import argparse
import logging
import os
import random
import re
import requests
import threading
from pathlib import Path
from pymongo import MongoClient
from read_sp500 import read_sp500


def get_working_proxies(path):
    with open(path, "r") as proxy_file:
        proxies = json.load(proxy_file)

    return proxies


def divide_in_chunks(alist: list, num: int):
    length = len(alist)
    chunk_size = (length // num)
    for i in range(0, length, chunk_size):
        yield alist[i: i+chunk_size]


def start_with_threads(sp500: list, proxies: list):
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


class ProxyList:
    def __init__(self, proxies: list):
        self.proxies = proxies
        random.shuffle(self.proxies)
        self.deleted_proxies = []
        self.index = random.randint(0, len(self.proxies) - 1)

    def delete_proxy(self):
        self.deleted_proxies.append(self.proxies[self.index])
        del self.proxies[self.index]
        logging.debug("%d proxies left", len(self.proxies))

        if len(self.proxies) == 0:  # if all proxies are deleted
            self.proxies = self.deleted_proxies
            self.deleted_proxies = []

        self.index = random.randint(0, len(self.proxies) - 1)

    def get_proxy(self):
        return self.proxies[self.index]


def add_messages_to_db(messages, collection):
    for post in messages:
        date_str = re.sub("Z", "", post["created_at"])
        post["date"] = datetime.datetime.fromisoformat(date_str)
        update_result = collection.update_one({"id": post["id"]},
                                              {"$set": post},
                                              upsert=True)
        logging.debug("update_one acknowledged: %s",
                      update_result.acknowledged)


def crawl(sp500_chunk, proxies):
    client = MongoClient()
    database = client["stocktwitsdb"]
    proxy_list = ProxyList(proxies)
    timeout = 15
    while True:
        for company in sp500_chunk:
            request_url = "https://api.stocktwits.com/api/2/streams/symbol/" \
                + company + ".json"
            successful = False
            while not successful:
                proxy = proxy_list.get_proxy()
                try:
                    result = requests.get(request_url,
                                          proxies={"https": proxy},
                                          timeout=timeout)

                except Exception as e:
                    logging.debug(str(e))
                    proxy_list.delete_proxy()
                    continue

                status_code = result.status_code
                if status_code == 200:  # request was successful
                    successful = True

                else:  # proxy worked but API did not response as wished
                    logging.debug("Requests was unsuccessful. Status code: %d",
                                  status_code)
                    proxy_list.delete_proxy()
                    continue

            result_json = result.json()
            messages = result_json["messages"]
            logging.info("%d results for %s", len(messages), company)

            # add all messages to the database
            add_messages_to_db(messages, database[company])


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
    random.shuffle(sp500)
    proxies = get_working_proxies(proxy_path)

    use_threading = args.threading
    if use_threading:
        start_with_threads(sp500, proxies)
    else:
        crawl(sp500, proxies)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Training parameters")
    parser.add_argument("--threading", action="store_true",
                        help="Only non-zero sentiments")
    args = parser.parse_args()

    main()
