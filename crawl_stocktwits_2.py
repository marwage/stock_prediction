import json
import sys
from datetime import timedelta, datetime
import time
from pymongo import MongoClient

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def get_proxies():
    user_agent = UserAgent()
    proxies = []

    # retrieve  proxies
    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', user_agent.random)
    proxies_doc = urlopen(proxies_req).read().decode('utf8')

    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = soup.find(id='proxylisttable')

    # save proxies in array
    for row in proxies_table.tbody.find_all('tr'):
      proxies.append({
        'ip':   row.find_all('td')[0].string,
        'port': row.find_all('td')[1].string
    })

    return proxies

    # Choose a random proxy
    proxy_index = random.randint(0, len(proxies) - 1)
    proxy = proxies[proxy_index]


def query_store(sp500, proxies):
    start_time = datetime.now()

    #mongodb
    client = MongoClient()
    db = client.stocktwitsdb

    for company in sp500:
        # pick random proxy
        proxy_index = random.randint(0, len(proxies) - 1)
        proxy = proxies[proxy_index]

        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"
        req = Request(request_url)
        req.set_proxy(proxy["ip"] + ":" + proxy["port"], "http")

        successful = False
        while not successful:
            try:
                result = urlopen(req).read().decode('utf8')
                print(type(result))
                successful = True
            except: # If error, delete this proxy and find another one
                del proxies[proxy_index]
                write_to_log("proxy " + proxy["ip"] + ":" + proxy["port"] + " deleted.")
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

    sp500 = read_sp500(sp500_path)
    proxies = get_proxies()
    query_store(sp500, proxies)

    write_to_log(str(datetime.now()) + " finished")


if __name__ == '__main__':
    main()


