import json
import requests
import random
from datetime import timedelta, datetime
from pymongo import MongoClient
from util import read_sp500
import threading
import queue


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


def write_to_log_thread(queue):
    log_path = "/home/wagenlaeder/stock-prediction/files/crawl_stocktwits_threading.log"

    end = datetime.now() + timedelta(hours=23)
    while datetime.now() < end:
        if not queue.empty():
            log = open(log_path, "a")
            log.write(str(datetime.now()) + " " + queue.get().replace("\n", " ") + "\n")
            log.close()


def crawl(company, proxies, log_queue):
    client = MongoClient()
    db = client.stocktwitsdb

    all_proxies = proxies.copy()
    random.shuffle(proxies)

    timeout = 30
    proxy_index = random.randint(0, len(proxies) - 1)
    proxy = proxies[proxy_index]
    
    request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"

    end = datetime.now() + timedelta(hours=23)
    while datetime.now() < end:
        successful = False
        while not successful:         
            try:
                result = requests.get(request_url, proxies=proxy, timeout=timeout)
                
                if result.status_code == 200: # request was successful
                    successful = True

                    log_queue.put(str(len(result.json()["messages"])) + " results for " + company)

                    # add all messages to the database
                    collection = db[company]
                    for post in result.json()["messages"]:
                        write_result = collection.update(post, post, upsert=True)
                else: # proxy worked but API did not response as wished
                    proxy_index = random.randint(0, len(proxies) - 1)
                    proxy = proxies[proxy_index]
            except Exception as e:
                log_queue.put(str(e))
                
                # delete the proxy that causes an exception from the list of proxies
                del proxies[proxy_index]

                log_queue.put(str(len(proxies)) + " proxies left")

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
    log_queue = queue.Queue()
    
    log_queue.put("start crawling stocktwits")

    sp500 = read_sp500(sp500_path)
    proxies = get_proxies(proxy_path)
    
    threads = []
    thread = threading.Thread(target=write_to_log_thread, name="log_thread", args=(log_queue,))
    thread.start()
    threads.append(thread)

    for company in sp500:
        thread = threading.Thread(target=crawl, name=company, args=(company, proxies.copy(), log_queue))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    write_to_log(log_path, "crawling stocktwits finished")


if __name__ == '__main__':
    main()


