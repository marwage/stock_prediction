import datetime
import json
import os
from pymongo import MongoClient


def sample_dates(data_set, data_set_name: str, output_path: str):
    dates = data_set.aggregate([{"$sample": {"size": 10}}])
    for i, date in enumerate(dates):
        del date["_id"]
        date["start"] = date["start"].isoformat()
        date["end"] = date["end"].isoformat()

        file_name = "sample_data_set_{}_{}.json".format(data_set_name, i)
        file_name = os.path.join(output_path, file_name)
        with open(file_name, "w") as tweet_file:
            json.dump(date, tweet_file, indent=4)


def main():
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)

    client = MongoClient()
    database = client["trainingdatasetdb"]
    data_set_name = "Ava"
    data_set = database[data_set_name]
    sample_dates(data_set, data_set_name, output_path)


if __name__ == "__main__":
    main()
