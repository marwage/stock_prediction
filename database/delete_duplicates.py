from pymongo import MongoClient


def delete_stocktwitsdb_duplicates():
    client = MongoClient()
    database = client.stocktwitsdb

    pipeline = [
        {"$group": {
            "_id": {
                "body": "$body",
                "created_at": "$created_at"
            },
            "uniqueIds": {"$addToSet": "$_id"},
            "count": {"$sum": 1}
            }
        },
        {"$match": {
            "count": {"$gt": 1}
            }
        }
        ]

    delete_duplicates(database, pipeline)


def delete_twitterdb_duplicates():
    client = MongoClient()
    database = client.twitterdb

    pipeline = [
        {"$group": {
            "_id": {
                "text": "$text",
                "created_at": "$created_at"
            },
            "uniqueIds": {"$addToSet": "$_id"},
            "count": {"$sum": 1}
            }
        },
        {"$match": {
            "count": {"$gt": 1}
            }
        }
        ]

    delete_duplicates(database, pipeline)


def delete_duplicates(database, pipeline):
    for collection_name in database.list_collection_names():
        for obj in database[collection_name].aggregate(pipeline):
            unique_ids = obj["uniqueIds"][0:len(obj["uniqueIds"]) - 1]
            database[collection_name].delete_many({"_id": {"$in": unique_ids}})


def main():
    delete_twitterdb_duplicates()
    # delete_stocktwitsdb_duplicates()


if __name__ == "__main__":
    main()
