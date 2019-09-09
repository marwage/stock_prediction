import json
import requests


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


def check_proxies(proxies):
    timeout = 30

    for proxy in proxies:
        request_url = "https://api.stocktwits.com/api/2/streams/symbol/AAPL.json"     
            
        try:
            result = requests.get(request_url, proxies=proxy, timeout=timeout)
        except Exception as e:
            proxies.remove(proxy)

    files_path = "files/"
    with open(files_path + "working_proxies.json", "w") as proxies_file:
        json.dump(proxies, proxies_file)


def main():
    files_path = "files/"
    proxy_path = files_path + "proxy_list.txt"

    proxies = get_proxies(proxy_path)
    check_proxies(proxies)


if __name__ == '__main__':
    main()


