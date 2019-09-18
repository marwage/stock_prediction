from pymongo import MongoClient


def delete_duplicates():
    client = MongoClient()
    db = client.stocktwitsdb

    pipeline = [
        {"$group": {
            "_id": {"body": "$body", "created_at": "$created_at"},
            "uniqueIds": {"$addToSet": "$_id"},
            "count": {"$sum": 1}
            }
        },
        {"$match": { 
            "count": {"$gt": 1}
            }
        }
        ]
   
    for collection_name in db.list_collection_names():
        for ob in db[collection_name].aggregate(pipeline):
            db[collection_name].delete_many( { "_id": { "$in": ob["uniqueIds"][0:len(ob["uniqueIds"]) - 1]}})


def main():
    delete_duplicates()


if __name__ == '__main__':
    main()
