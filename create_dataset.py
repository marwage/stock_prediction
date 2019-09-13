from pymongo import MongoClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import sys
import nltk
nltk.download('vader_lexicon')


def create_dataset():
    client = MongoClient()
    db = client.stocktwitsdb
    sid = SentimentIntensityAnalyzer()

    for share_code in db.list_collection_names():
        for ob in db[share_code].find(filter={}, projection={"body"}):
            print(type(ob))

        sentences = ["VADER is smart, handsome, and funny."]

        for sentence in sentences:
            print(sentence)
            ss = sid.polarity_scores(sentence)
            for k in sorted(ss):
                print("{0}: {1}, ".format(k, ss[k]), end="")


if __name__ == '__main__':
    create_dataset()