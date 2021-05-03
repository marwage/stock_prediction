import datetime
import json
import os
import random
from pymongo import MongoClient


def sample_infos(database, output_path: str):
    companies = database.list_collection_names()
    num_companies = len(companies)
    num_samples = 10
    for _ in range(num_samples):
        index = random.randint(0, num_companies)
        company_name = companies[index]
        company = database[company_name]
        company_info = company.find_one({})
        del company_info["_id"]
        file_name = "sample_company_info_{}.json".format(company_name)
        file_name = os.path.join(output_path, file_name)
        with open(file_name, "w") as sample_file:
            json.dump(company_info, sample_file, indent=4)


def main():
    output_path = os.path.join(".", "output")
    os.makedirs(output_path, exist_ok=True)

    client = MongoClient()
    database = client["companyinfodb"]
    sample_infos(database, output_path)


if __name__ == "__main__":
    main()
