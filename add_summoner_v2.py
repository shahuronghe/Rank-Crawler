from riotwatcher import LolWatcher, ApiError
import json
import os
from pymongo import MongoClient

'''
When The Summoner is getting added the last Match also has to be added
so that the program can check if a new match has been played.
'''

def get_api_key():
    """Get the API key from the environment variable."""
    api_key = os.getenv('RIOT_API_KEY')
    return api_key

def get_mongodb_pw():
    """Get the MongoDB password from the environment variable."""
    mongodb_pw = os.getenv('MONGODB_PW')
    return mongodb_pw

def connect_to_mongodb(mongodb_pw):
    """Connect to MongoDB Atlas."""
    CONNECTION_STRING = f'mongodb+srv://user:{mongodb_pw}@rank-crawler.kvodu7l.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(CONNECTION_STRING)
    return client

def get_summoner_info():
    """Get the summoner name and region from the user."""
    summoner_name_input = input('Enter summoner name: ')
    while not summoner_name_input:
        print('You must enter a summoner name.')
        summoner_name_input = input('Enter summoner name: ')

    # BR1, EUN1, EUW1, JP1, KR, LA1, LA2, NA1, OC1, TR1, RU, PH2, SG2, TH2, TW2, VN2
    summoner_region_input = input('Enter region: ')
    while not summoner_name_input:
        print('You must enter a region.')
        summoner_region_input = input('Enter region: ')

    return summoner_name_input, summoner_region_input


def add_summoner(watcher, client, summoner_name, summoner_region):
    summoner = watcher.summoner.by_name(summoner_region, summoner_name)
    my_matches = watcher.match.matchlist_by_puuid(summoner_region, summoner['puuid'])
    last_match_id = my_matches[0]
    rank_crawler_db = client['rank-crawler']

    existing_summoner = rank_crawler_db.summoner.find_one({'puuid': summoner['puuid']})

    if existing_summoner:
        print(f'Summoner {summoner_name} already exists in the database.')
        return

    summoner_data = summoner
    summoner_data['matches'] = []
    summoner_data['matches'].insert(0, last_match_id)

    rank_crawler_db.summoner.insert_one(summoner_data)
    
    last_match = watcher.match.by_id(summoner_region, last_match_id)
    rank_crawler_db.match.insert_one(last_match)

if __name__ == '__main__':
    api_key = get_api_key()
    watcher = LolWatcher(api_key)
    mongodb_pw = get_mongodb_pw()
    client = connect_to_mongodb(mongodb_pw)
    summoner_name, summoner_region = get_summoner_info()
    add_summoner(watcher, client, summoner_name, summoner_region)