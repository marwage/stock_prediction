import json
import requests
from pymongo import MongoClient


def try_update():
    client = MongoClient()
    db = client.stocktwitsdb

    request_url = "https://api.stocktwits.com/api/2/streams/symbol/AAPL.json"     
        
    try:
        result = requests.get(request_url)

        if result.status_code == 200: # request was successful
            # add all messages to the database
            collection = db["AAPL"]
            for post in result.json()["messages"]:
                write_result = collection.update({"body": post["body"], "created_at": post["created_at"]} , post, upsert=True)
                print(str(post)[0:20])
    except Exception as e:
        print(e)


def main():
    try_update()


if __name__ == '__main__':
    main()