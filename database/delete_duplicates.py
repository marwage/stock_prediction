from pymongo import MongoClient


def delete_stocktwitsdb_duplicates():
    client = MongoClient()
    db = client.stocktwitsdb

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
   
    delete_duplicates(db, pipeline)


def delete_twitterdb_duplicates():
    client = MongoClient()
    db = client.twitterdb

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
   
   delete_duplicates(db, pipeline)


def delete_duplicates(db, pipeline):
    for collection_name in db.list_collection_names():
        for ob in db[collection_name].aggregate(pipeline):
            db[collection_name].delete_many( { "_id": { "$in": ob["uniqueIds"][0:len(ob["uniqueIds"]) - 1]}})


def main():
    delete_twitterdb_duplicates()
    #delete_stocktwitsdb_duplicates()


if __name__ == '__main__':
    main()
