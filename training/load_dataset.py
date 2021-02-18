import numpy as np
from pymongo import MongoClient
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


class CompanyDB(Dataset):
    def __init__(self, db_name, collection_name, transform=None):
        self._label_dtype = np.float32
        self.transform = transform

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
        id = self.inputs[i]["_id"]
        document = self.collection.find_one({"_id": _id})

        sentiments = [pair["sentiment"] for pair in document["tweets"]]

        if self.transform:
            sentiments = self.transform(sentiments)

        label = self.labels[i]
        return sentiments, label, id


def main():
    transform = transforms.Compose([
            transforms.ToTensor()
        ])

    dataset = CompanyDB("learing", "AAPL", transform=transform)
    loader = DataLoader(dataset, batch_size=256, shuffle=True, num_workers=8)
    for sentiment, label, id in loader:
        print(sentiment)
        print("+++")
        print(label)
        print("---")


if __name__ == "__main__":
    main()
