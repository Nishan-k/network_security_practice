from pymongo import MongoClient
from dotenv import load_dotenv
import os




# 1. Load the .env file:
load_dotenv()

# Get the URI from environment
mongo_uri = os.getenv("MONGO_DB_URL")


# Debug: print the URI to confirm
if not mongo_uri:
    print("MONGO_DB_URL not found in the .env file.")
    exit()

# Connect to MongoDB Atlas
client = MongoClient(mongo_uri)


# Test the connection:
try:
    client.admin.command("ping")
    print("Pinged the cluster at MongoDB. You have successfully connected to the MongoDB.")
except Exception as e:
    print(f"Connection failed: {e}")