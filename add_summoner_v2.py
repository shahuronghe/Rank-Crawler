from dotenv import load_dotenv
import os
import sys

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from riotwatcher import LolWatcher, ApiError

from utils.routing import platform_to_cass_region, platform_to_cass_continent

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

lol_watcher = LolWatcher(RIOT_API_KEY)


def save_summoner(summoner_name: str, platform: str):
    '''Saves a summoner to the database.'''
    # Ckeck if summoner is already in database
    collection = client['rank-crawler']['summoners']
    summoner = collection.find_one({'name': summoner_name, 'platform': platform})
    if summoner:
        print('Summoner already in database!')
        return


    # Get summoner data
    summoner = lol_watcher.summoner.by_name(platform, summoner_name)
    summoner['platform'] = platform


    # Get the league data
    league_entries = lol_watcher.league.by_summoner(platform, summoner['id'])

    # Merge the league data into the summoner data
    summoner['league_entries'] = league_entries

    # Save summoner to database
    summoner_collection = client['rank-crawler']['summoners']
    summoner_collection.insert_one(summoner)


save_summoner('G5 Easy', 'euw1')