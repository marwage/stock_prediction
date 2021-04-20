import logging
import os
import sys
from pathlib import Path
from pymongo import MongoClient


def check_duplicates():
    client = MongoClient()
    database = client["twitterdb"]

    pipeline = [
        {"$group": {
            "_id": {
                "id": "$id",
            },
            "object_ids": {"$addToSet": "$_id"},
            "count": {"$sum": 1}
            }
        },
        {"$match": {
            "count": {"$gt": 1}
            }
        }
        ]

    for company in database.list_collection_names():
        logging.debug("Looking into %s", company)
        collection = database[company]
        cursor = collection.aggregate(pipeline, allowDiskUse=True)
        for match in cursor:
            logging.info("Found duplicate: %s", match)
            for object_id in match["object_ids"]:
                tweet = collection.find_one({"_id": object_id})
                logging.debug("Tweet %s: id %s, date %s",
                              tweet["_id"], tweet["id"], tweet["date"])
            print("Press a key to continue")
            input()


def main():
    if sys.platform == "linux":
        path = os.path.join(Path.home(), "stock-prediction")
    else:
        directory = "Studies/Master/10SS19/StockPrediction/stock-prediction"
        path = os.path.join(Path.home(), directory)
    log_path = os.path.join(path, "database/log/check_duplicates.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    check_duplicates()


if __name__ == "__main__":
    main()
