import pymongo
import json
import twitter
from datetime import date, timedelta

def main():
	client = MongoClient()
	db = client.twitter
	collection = db.aapl

	###
	with open("access_token.json") as access_token_file:
		json_object = json.load(access_token_file)

	api = twitter.Api(consumer_key=json_object["consumer_key"],
                  consumer_secret=json_object["consumer_secret"],
                  access_token_key=json_object["access_token_key"],
                  access_token_secret=json_object["access_token_secret"])

	company_abbreviation = "aapl"
	since = date.today() - timedelta(days=1)
	until = date.today()
	query = "q=" + company_abbreviation + "%20since%3A" + str(since) + "%20until%3A" + str(until)
	results = api.GetSearch(raw_query=query)
	###

	result = collection.insert_many(results)
	print(result.inserted_ids)


if __name__ == '__main__':
	main()