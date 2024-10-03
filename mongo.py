import json
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import InsertOne


class Mongo:
    def __init__(self):
        self.uri = os.getenv('CONNECTION_STRING')

        # Create a new client and connect to the server
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        self.db = self.client['LotteryScanner']
        self.collection = self.db['Records']
        self.folders = [x[0] for x in os.walk('output') if x[0] != 'output']

    def close(self):
        self.client.close()

    def insert_latest_record(self):
        datelist = [f.split('output/')[1] for f in self.folders]

        latest_date = max(datelist)
        print(latest_date)
        output_path = f'output/{latest_date}/records.json'
        with open(output_path, 'r') as j:
            data = json.load(j)

        self.collection.InsertOne(data)

    def insert_all(self):
        operations = []
        for f in self.folders:
            output = f'{f}/records.json'
            with open(output, 'r') as j:
                operations.append(InsertOne(json.load(j)))

        self.collection.bulk_write(operations)


def run_Mongo():
    mongo = Mongo()
    mongo.insert_all()

run_Mongo()