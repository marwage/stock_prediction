import datetime
import json
from pymongo import MongoClient


def sample_dates(data_set, data_set_name: str):
    dates = data_set.aggregate([{"$sample": {"size": 10}}])
    for i, date in enumerate(dates):
        del date["_id"]
        date["start"] = date["start"].isoformat()
        date["end"] = date["end"].isoformat()

        file_name = "output/sample_data_set_{}_{}.json".format(data_set_name,
                                                               i)
        with open(file_name, "w") as tweet_file:
            json.dump(date, tweet_file, indent=4)


def main():
    client = MongoClient()

    database = client["trainingdatasetdb"]
    data_set_name = "Ava"
    data_set = database[data_set_name]
    sample_dates(data_set, data_set_name)


if __name__ == "__main__":
    main()
