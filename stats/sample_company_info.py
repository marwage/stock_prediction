import datetime
import json
from pymongo import MongoClient
import random


def sample_infos(database):
    companies = database.list_collection_names()
    num_companies = len(companies)
    num_samples = 10
    for _ in range(num_samples):
        index = random.randint(0, num_companies)
        company_name = companies[index]
        company = database[company_name]
        company_info = company.find_one({})
        del company_info["_id"]
        file_name = "output/sample_company_info_{}.json".format(company_name)
        with open(file_name, "w") as sample_file:
            json.dump(company_info, sample_file, indent=4)


def main():
    client = MongoClient()

    database = client["companyinfodb"]
    sample_infos(database)


if __name__ == "__main__":
    main()
