from pymongo import MongoClient
from datetime import datetime
import json


def main():
    client = MongoClient()
    
    # stocktwits
    db = client.stocktwitsdb

    stats = dict()
    for share_code in db.list_collection_names():
        collection = db[share_code]
        stats[share_code] = dict()
        for post in collection.find({}):
            date_string = post['created_at']
            post_date = datetime.strptime(date_string[0:10], '%Y-%m-%d')
            date_string = post_date.strftime('%Y-%m-%d')
            if date_string in stats[share_code]:
                stats[share_code][date_string] = stats[share_code][date_string] + 1
            else:
                stats[share_code][date_string] = 1

    with open('files/stocktwits_stats.json', 'w') as json_file:
        json.dump(stats, json_file)


if __name__ == '__main__':
    main()
