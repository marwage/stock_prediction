import numpy as np
from pymongo import MongoClient
import torch
from torch.utils.data import Dataset, DataLoader


class CompanyDB(Dataset):
    def __init__(self, db_name, collection_name):
        self._label_dtype = np.float32

        client = MongoClient("localhost", 27017)
        db = client[db_name]
        self.collection = db[collection_name]
        self.inputs = list(self.collection.find({}))

        self.labels = self.get_labels()

    def __len__(self):
        return len(self.inputs)

    def get_labels(self):
        return [input["price_diff"] for input in self.inputs]

    def __getitem__(self, i):
        _id = self.inputs[i]["_id"]
        document = self.collection.find_one({"_id": _id})

        sentiments = [pair["sentiment"] for pair in document["tweets"]]
        sentiments = torch.Tensor(sentiments)

        label = self.labels[i]
        return sentiments, label, _id


def main():
    dataset = CompanyDB("learning", "AAPL")
    loader = DataLoader(dataset, batch_size=256, shuffle=True, num_workers=8)
    for sentiment, label, _id in loader:
        print(sentiment)
        print("+++")
        print(label)
        print("---")


if __name__ == "__main__":
    main()
