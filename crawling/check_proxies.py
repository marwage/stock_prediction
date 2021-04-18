import json
import logging
import os
import requests
import sys
from pathlib import Path


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


def check_proxies(proxies, output_path):
    timeout = 12
    num_proxies = len(proxies)

    for i, proxy in enumerate(proxies):
        logging.debug("check proxy %d/%d", i, num_proxies)

        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" \
            + "AAPL.json"

        try:
            _ = requests.get(request_url, proxies=proxy, timeout=timeout)
        except Exception as e:
            proxies.remove(proxy)

    with open(output_path, "w") as proxies_file:
        json.dump(proxies, proxies_file, indent="\t")


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        print("Wrong OS")
        return
    crawling_path = os.path.join(path, "crawling")
    log_path = os.path.join(crawling_path, "log/check_proxies.log")
    proxy_path = os.path.join(crawling_path, "data/proxy_list.txt")
    output_path = os.path.join(crawling_path, "data/working_proxies.json")

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    proxies = get_proxies(proxy_path)
    check_proxies(proxies, output_path)


if __name__ == '__main__':
    main()
