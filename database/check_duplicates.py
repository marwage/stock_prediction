import argparse
import logging
import os
import sys
from pymongo import MongoClient


def check_duplicates():
    client = MongoClient()
    databases = [client["stocktwitsdb"], client["twitterdb"]]

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

    for database in databases:
        for company in database.list_collection_names():
            logging.debug("Looking into %s", company)
            collection = database[company]
            cursor = collection.aggregate(pipeline, allowDiskUse=True)
            for match in cursor:
                logging.info("Found duplicate: %s", match)
                if args.delete:
                    set_size = len(match["object_ids"])
                    delete_set = match["object_ids"][0:set_size - 1]
                    filtr = {"_id": {"$in": delete_set}}
                    delete_result = collection.delete_many(filtr)
                    logging.debug("Deleted %d objects",
                                  delete_result.deleted_count)


def main():
    log_path = os.path.join(".", "log/check_duplicates.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s:%(message)s"
        )

    check_duplicates()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training parameters")
    parser.add_argument("--delete", action="store_true",
                        help="Delete duplicates")
    args = parser.parse_args()

    main()
