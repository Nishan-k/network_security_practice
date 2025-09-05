import pandas as pd
import json
import os
import sys
from dotenv import load_dotenv
import certifi
import numpy as np
import pymongo
from networksecurity.logging import logger
from networksecurity.exception.exception import NetworkSecurityException


# Load .env file
load_dotenv()

# Get the URI from environment
mongo_uri = os.getenv("MONGO_DB_URL")


ca = certifi.where()



class NetworkDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def csv_to_json_converter(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    
    def insert_data_to_mongodb(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            self.mongo_client = pymongo.MongoClient(mongo_uri)
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)
            return (len(self.records))
        except Exception as e:
            raise NetworkSecurityException(e, sys)



if __name__ == "__main__":
    FILE_PATH = "Network_Data\phisingData.csv"
    DATABASE = "network_security"
    COLLECTIONS = "network_security_collection"
    network_data_obj = NetworkDataExtract()
    records = network_data_obj.csv_to_json_converter(file_path=FILE_PATH)
    no_of_records = network_data_obj.insert_data_to_mongodb(records=records, database=DATABASE, collection=COLLECTIONS)
    print(f"A total number of {no_of_records} records were inserted in the {DATABASE} data on the collection: {COLLECTIONS}")