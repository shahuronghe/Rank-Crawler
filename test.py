from dotenv import load_dotenv
import os
from enum import Enum
from datetime import datetime

import requests

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from utils.routing import platform_to_region

# Setup
load_dotenv()
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Replace the placeholder with your Atlas connection string
uri = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0.cgxkcwy.mongodb.net/?retryWrites=true&w=majority"

# Set the Stable API version when creating a new client
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged MongoDB!")
except Exception as e:
    print(e)


def save_match(match_id, platform):
    """
    Get the match data from the Riot API
    for each summoner in the match that is in the database get the rank data and add it to the match data
    
    example:
    participants[0]["rank"] = {
        "tier": "PLATINUM",
        "rank": "I",
        "leaguePoints": 100,
    }
    """
    url = f"https://{platform_to_region(platform)}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    match_data = response.json()

    collection = client["rank-crawler"]["matches"]

    # Check if match already exists in database
    match = collection.find_one({"metadata.matchId": match_data["metadata"]["matchId"]})
    if match:
        print("    Match already exists in database")
        return
    
    # Check if the match is a ranked match
    if match_data["info"]["queueId"] == 420 or match_data["info"]["queueId"] == 440:
        for participant in match_data["info"]["participants"]:
            # check if summoner is in database
            summoner = client["rank-crawler"]["summoners"].find_one({"id": participant["summonerId"]})
            if summoner:
                if match_data["info"]["queueId"] == 420:
                    for rank in summoner["rank"]:
                        if rank["queueType"] == "RANKED_SOLO_5x5":
                            participant["rank"] = {
                                "tier": rank["tier"],
                                "rank": rank["rank"],
                                "leaguePoints": rank["leaguePoints"],
                            }
                elif match_data["queueId"] == 440:
                    for rank in summoner["rank"]:
                        if rank["queueType"] == "RANKED_FLEX_SR":
                            participant["rank"] = {
                                "tier": rank["tier"],
                                "rank": rank["rank"],
                                "leaguePoints": rank["leaguePoints"],
                            }
            else:
                participant["rank"] = None

    # Add match to database
    collection.insert_one(match_data)
    print("    Added match to database")


    url = f"https://{platform_to_region(platform)}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    timeline_data = response.json()
    
    
    collection = client["rank-crawler"]["timelines"]

    # Check if timeline already exists in database
    timeline = collection.find_one({"metadata.matchId": timeline_data["metadata"]["matchId"]})
    if timeline:
        print("    Timeline already exists in database")
        return
    
    # Add timeline to database
    collection.insert_one(timeline_data)
    print("    Added timeline to database")


def update_summoner(summoner_name, platform):
    """
    Get the summoner data from the Riot API and update the rank data in the database
    """
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    summoner_data = response.json()

    summoners_collection = client["rank-crawler"]["summoners"]

    print("    Getting rank data")
    # Get rank
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_data['id']}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    rank_data = response.json()
    
    # remove unnecessary data from rank_data
    if rank_data:
        for rank in rank_data:
            rank.pop("summonerId")
            rank.pop("summonerName")

    # Add rank to summoner_data
    summoner_data["rank"] = rank_data

    # Check if summoner exists in database
    summoner = summoners_collection.find_one({"id": summoner_data["id"]})
    if not summoner:
        print("    Summoner is not added to database")
        return
    
    summoner.pop("_id")
    if sorted(summoner) == sorted(summoner_data):
        print("    Summoner is up to date")
        pass

    else:
        summoners_collection.update_one({"id": summoner_data["id"]}, {"$set": summoner_data})
        print("    Updated summoner data")

    # check if summoner has played new matches
    # TODO replace the static europe with the platform
    url = f"https://{platform_to_region(platform)}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_data['puuid']}/ids?start=0&count=1&api_key={RIOT_API_KEY}"
    response = requests.get(url)
    match_ids = response.json()

    matches_collection = client["rank-crawler"]["matches"]

    # Check if summoner has played new matches
    if matches_collection.find_one({"metadata.matchId": match_ids[0]}):
        print("    Summoner has not played new matches")
        return
    
    # Get the match data
    save_match(match_ids[0], platform)


def update_all_summoners():
    """
    Update all summoners in the database
    """
    summoners_collection = client["rank-crawler"]["summoners"]
    summoners = summoners_collection.find()
    for summoner in summoners:
        print(f"Updating {summoner['name']}")
        update_summoner(summoner["name"], summoner["platform"])


def main():
    update_all_summoners()


if __name__ == "__main__":
    main()
