from dotenv import load_dotenv
import os
import sys

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import cassiopeia as cass

from utils.routing import platform_to_cass_region

# Setup
load_dotenv()
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

uri = f'mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0.cgxkcwy.mongodb.net/?retryWrites=true&w=majority'

# Set the Stable API version when creating a new client
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print('Pinged MongoDB!')
except Exception as e:
    print(e)

cass.set_riot_api_key(RIOT_API_KEY)


def save_summoner(summoner_name: str, platform: str):
    # Ckeck if summoner is already in database
    '''
    collection = client['rank-crawler']['summoners']
    summoner = collection.find_one({'name': summoner_name, 'platform': platform})
    if summoner:
        print('Summoner already in database!')
        return
    '''

    # Get summoner data from Riot API
    cass_summoner = cass.get_summoner(name=summoner_name, region=platform_to_cass_region(platform))

    cass_summoner.load()
    print(cass_summoner)

save_summoner('G5 Easy', 'euw1')