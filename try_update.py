import json
import requests
from pymongo import MongoClient


def try_update():
    client = MongoClient()
    db = client.stocktwitsdb
    collection = db["GOOGL"]

    request_url = "https://api.stocktwits.com/api/2/streams/symbol/GOOGL.json"     
        
    try:
        result = requests.get(request_url)
        if result.status_code == 200: # request was successful
            # add all messages to the database
            for post in result.json()["messages"]:
                query = {
                    "body": post["body"],
                    "created_at": post["created_at"]
                    }
                write_result = collection.update(query , post, upsert=True)
                print(write_result)
    except Exception as e:
        print(e)


def main():
    try_update()


if __name__ == '__main__':
    main()
