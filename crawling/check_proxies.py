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


def check_proxies(proxies, output_path):
    timeout = 9

    for proxy in proxies:
        request_url = "https://api.stocktwits.com/api/2/streams/symbol/AAPL.json"     
            
        try:
            result = requests.get(request_url, proxies=proxy, timeout=timeout)
        except Exception as e:
            proxies.remove(proxy)

    with open(output_path, "w") as proxies_file:
        json.dump(proxies, proxies_file, indent=4)


def main():
    # paths are relative
    proxy_path = "data/proxy-list.txt"
    output_path = "data/working-proxies.json"

    proxies = get_proxies(proxy_path)
    check_proxies(proxies)


if __name__ == '__main__':
    main()


