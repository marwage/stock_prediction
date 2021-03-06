from pymongo import MongoClient
import json


def aggregate_stats():
    client = MongoClient()
    learning_db = client["learning"]
    
    collection_names = learning_db.list_collection_names()
    num_companies = len(collection_names)
    print("Number of companies: {}".format(num_companies))

    stats = dict()
    for company in collection_names:
        collection = learning_db[company]
        stats[company] = dict()
        stats[company]["days"] = collection.count_documents({})

    with open("stats.json", "w") as json_file:
        json.dump(stats, json_file, indent=4)


def main():
    aggregate_stats()


if __name__ == "__main__":
    main()

