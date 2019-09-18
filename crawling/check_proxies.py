import json
import requests
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


def check_proxies(proxies, output_path):
    timeout = 9
    num_proxies = len(proxies)

    for i, proxy in enumerate(proxies):
        logging.debug("check proxy " + str(i) + "/" + str(num_proxies))

        request_url = "https://api.stocktwits.com/api/2/streams/symbol/AAPL.json"     
            
        try:
            result = requests.get(request_url, proxies=proxy, timeout=timeout)
        except Exception as e:
            proxies.remove(proxy)

    with open(output_path, "w") as proxies_file:
        json.dump(proxies, proxies_file, indent=4)


def main():
    crawling_path = "stock-prediction/crawling/"
    proxy_path = crawling_path + "data/proxy_list.txt"
    output_path = crawling_path + "data/working_proxies.json"
    log_path = crawling_path + "log/crawl_alpha_vantage.log"

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    proxies = get_proxies(proxy_path)
    check_proxies(proxies)


if __name__ == '__main__':
    main()


