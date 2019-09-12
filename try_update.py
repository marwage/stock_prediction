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
                query = dict()
                query["body"] = post["body"]
                query["created_at"] = post["created_at"]
                for ob in collection.find(query):
                    print(ob)
                write_result = collection.update(query , post, upsert=True)
    except Exception as e:
        print(e)


def main():
    try_update()


if __name__ == '__main__':
    main()