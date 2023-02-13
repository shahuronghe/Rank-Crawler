from dotenv import load_dotenv, find_dotenv
import os
import pprint
import json
from pymongo import MongoClient

load_dotenv(find_dotenv())

MONGODB_PW = os.getenv("MONGODB_PW")

CONNECTION_STRING = f"mongodb+srv://user:{MONGODB_PW}@rank-crawler.kvodu7l.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)

test_db = client.test

def insert_json_file():
    with open("EUW1_6273005604.json", "r") as f:
        summoner = json.load(f)
    return test_db.test.insert_one(summoner).inserted_id

def insert_data():
    data = {
        "name": "test",
        "age": 20
    }
    return test_db.test.insert_one(data).inserted_id


rank_crawler_db = client["rank-crawler"]
summmoner_collection = rank_crawler_db["summoner"]
match_collection = rank_crawler_db["match"]

def create_documents():
    docs = []
    for i in range(10):
        doc = {
            "name": f"test_{i}",
            "age": i
        }
        docs.append(doc)
    match_collection.insert_many(docs)

create_documents()