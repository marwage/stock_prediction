from pymongo import MongoClient


def main():
	client = MongoClient()
    
    # stocktwits
    db = client.stocktwitsdb

    stats = dict()
	for share_code in db.list_collection_names():
		collection = db.share_code
		stats[share_code] = dict()
		for post in collection.find():
			date_string = post['created_at']
			date = datetime.strptime(date_string[0:10], '%Y-%m-%d')
			if date in stats[share_code]:
				stats[share_code][date] = stats[share_code][date] + 1
			else:
				stats[share_code][date] = 1


if __name__ == '__main__':
	main()