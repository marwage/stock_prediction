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
        proxies.append("http://" + row)

    return proxies


def check_proxies(proxies, output_path):
    timeout = 12
    num_proxies = len(proxies)
    working_proxies = []

    for i, proxy in enumerate(proxies):
        logging.debug("check proxy %d/%d", i, num_proxies)

        successful = True
        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" \
            + "AAPL.json"
        try:
            _ = requests.get(request_url,
                             proxies={"https": proxy},
                             timeout=timeout)
        except Exception as e:
            logging.debug("Requests exception: %s", str(e))
            successful = False

        if successful:
            working_proxies.append(proxy)

    with open(output_path, "w") as proxies_file:
        json.dump(working_proxies, proxies_file, indent="\t")


def main():
    log_path = os.path.join(".", "log/check_proxies.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    proxy_path = os.path.join(".", "data/proxy_list.txt")
    output_path = os.path.join(".", "data/working_proxies.json")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    proxies = get_proxies(proxy_path)
    check_proxies(proxies, output_path)


if __name__ == '__main__':
    main()
