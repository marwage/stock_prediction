from pymongo import MongoClient
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import sys
import nltk
nltk.download('vader_lexicon')


def create_dataset():
    client = MongoClient()
    db = client.stocktwitsdb
    sid = SentimentIntensityAnalyzer()
    sentences = []

    for share_code in db.list_collection_names():
        for ob in db[share_code].find(filter={}, projection={"body"}):
            sentences.append(ob["body"])

        for sentence in sentences:
            print(sentence)
            ss = sid.polarity_scores(sentence)
            print(ss)


if __name__ == '__main__':
    create_dataset()
