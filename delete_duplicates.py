from pymongo import MongoClient


def delete_duplicates():
    client = MongoClient()
    db = client.stocktwitsdb

    pipeline = [
        {"$group": {
            "_id": {"body": "$body", "created_at": "$created_at"},
            "uniqueIds": {$addToSet: "$_id"},
            "count": {$sum: 1}
            }
        },
        {$match: { 
            count: {"$gt": 1}
            }
        }
        ]
    
    for collection in db.list_collection_names():
        print(collection.aggregate(pipeline))


def main():
    delete_duplicates()


if __name__ == '__main__':
    main()