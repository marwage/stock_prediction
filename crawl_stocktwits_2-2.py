import json
from datetime import timedelta, datetime
from pymongo import MongoClient


def read_sp500(path):
    with open(path, "r") as json_file:
        sp500_json = json.load(json_file)

    return sp500_json["sp500"]


def query_store(sp500):
    start_time = datetime.now()
    client = MongoClient()
    db = client.stocktwitsdb
    proxies = {
        'http': 'http://35.231.212.6:443',
        'https': 'http://35.231.212.6:443',
    }

    for company in sp500:

        request_url = "https://api.stocktwits.com/api/2/streams/symbol/" + company + ".json"
        result = requests.get(request_url, proxies=proxies)
        write_to_log(result)


def write_to_log(text):
    log_path = "files/crawl_stocktwits_2-2.log"
    
    with open(log_path, "a") as log:
        log.write(text + "\n")

    return


def main():
    sp500_path = "files/sp500.json"
    proxy_path = "files/proxy_list_2.txt"

    write_to_log(str(datetime.now()) + " started")

    sp500 = read_sp500(sp500_path)
    query_store(sp500)

    write_to_log(str(datetime.now()) + " finished")


if __name__ == '__main__':
    main()


