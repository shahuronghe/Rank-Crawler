from riotwatcher import LolWatcher, ApiError
import json
import os
from pymongo import MongoClient

'''
When The Summoner is getting added the last Match also has to be added
so that the program can check if a new match has been played.
'''

api_key = os.getenv('RIOT_API_KEY')
watcher = LolWatcher(api_key)
mongodb_pw = os.getenv('MONGODB_PW')

CONNECTION_STRING = f'mongodb+srv://user:{mongodb_pw}@rank-crawler.kvodu7l.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(CONNECTION_STRING)

summoner_name_input = input('Enter summoner name: ')
summoner_region_input = input('Enter region: ')
# BR1, EUN1, EUW1, JP1, KR, LA1, LA2, NA1, OC1, TR1, RU, PH2, SG2, TH2, TW2, VN2




def add_summoner(summoner_name, summoner_region):
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


add_summoner(summoner_name_input, summoner_region_input)