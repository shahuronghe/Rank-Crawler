from riotwatcher import LolWatcher, ApiError
import json
import os
from pymongo import MongoClient

api_key = os.getenv('RIOT_API_KEY')
watcher = LolWatcher(api_key)
mongodb_pw = os.getenv('MONGODB_PW')

CONNECTION_STRING = f'mongodb+srv://user:{mongodb_pw}@rank-crawler.kvodu7l.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(CONNECTION_STRING)

def get_last_match_id(summoner_region, summoner_puuid):
    my_matches = watcher.match.matchlist_by_puuid(summoner_region, summoner_puuid)
    return my_matches[0]

def add_summoner_to_db(summoner_data):
    rank_crawler_db = client['rank-crawler']
    rank_crawler_db.summoner.insert_one(summoner_data)

def get_summoner_rank(summoner_region, summoner_id):
    summoner_rank = watcher.league.by_summoner(summoner_region, summoner_id)
    return summoner_rank

def add_last_match_to_db(last_match):
    rank_crawler_db = client['rank-crawler']
    # If the match is a Ranked game 420 or 440
    # for every participant in the match
    # check if the summoner is saved in the database
    # if yes get the current rank for the summoner and save it to the participant object
    # queueType = RANKED_FLEX_SR == [0]
    # queueType = RANKED_SOLO_5x5 == [1]
    if last_match['info']['queueId'] == 420:
        for participant in last_match['info']['participants']:
            summoner = rank_crawler_db.summoner.find_one({'puuid': participant['puuid']})
            if summoner:
                league = get_summoner_rank(summoner_region_input, summoner['id'])[1]
                tier = league['tier']
                rank = league['rank']
                leaguePoints = league['leaguePoints']

                participant['rank'] = {
                    'tier': tier,
                    'rank': rank,
                    'leaguePoints': leaguePoints
                }
    rank_crawler_db.match.insert_one(last_match)


def add_summoner(summoner_name, summoner_region):
    summoner = watcher.summoner.by_name(summoner_region, summoner_name)
    last_match_id = get_last_match_id(summoner_region, summoner['puuid'])

    rank_crawler_db = client['rank-crawler']
    existing_summoner = rank_crawler_db.summoner.find_one({'puuid': summoner['puuid']})

    if existing_summoner:
        print(f'Summoner {summoner_name} already exists in the database.')
        return

    summoner_data = summoner
    summoner_data['matches'] = []
    summoner_data['matches'].insert(0, last_match_id)

    add_summoner_to_db(summoner_data)

    last_match = watcher.match.by_id(summoner_region, last_match_id)
    add_last_match_to_db(last_match)

summoner_name_input = input('Enter summoner name: ')
summoner_region_input = input('Enter region: ')
add_summoner(summoner_name_input, summoner_region_input)
