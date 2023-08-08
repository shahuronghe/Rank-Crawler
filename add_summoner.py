import requests
from dotenv import load_dotenv
import os
import sys

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

def save_matches(summoner_name, platform):
    """
    Get all matches from a summoner and save them to the database
    TO the latest soloq and flexq match add the rank of the summoner

    example:
    participants[0]["rank"] = {
        "tier": "PLATINUM",
        "rank": "I",
        "leaguePoints": 100,
    }
    """
    first_soloq_match = True
    first_flexq_match = True

    # Get summoner data from database
    collection = client["rank-crawler"]["summoners"]
    summoner = collection.find_one({"name": summoner_name, "platform": platform})

    # Get all matches from summoner
    start = 0
    count = 100
    while True:
        url = f"https://{platform_to_region(platform)}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner['puuid']}/ids?start={start}&count={count}&api_key={RIOT_API_KEY}"
        response = requests.get(url)
        match_ids = response.json()

        # If there are no more matches, break
        if not match_ids:
            break

        # Get match data for each match
        for match_id in match_ids:
            url = f"https://{platform_to_region(platform)}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
            response = requests.get(url)
            match_data = response.json()

            # Add rank to soloq match
            if first_soloq_match and match_data["info"]["queueId"] == 420:
                first_soloq_match = False
                for rank in summoner["rank"]:
                    if rank["queue"] == "RANKED_SOLO_5x5":
                        match_data["rank"] = {
                            "tier": rank["tier"],
                            "division": rank["division"],
                            "leaguePoints": rank["leaguePoints"],
                        }

            # Add rank to flexq match
            if first_flexq_match and match_data["info"]["queueId"] == 440:
                first_flexq_match = False
                for rank in summoner["rank"]:
                    if rank["queue"] == "RANKED_FLEX_SR":
                        for participant in match_data["info"]["participants"]:
                            if participant["summonerName"] == summoner_name:
                                participant["rank"] = {
                            "tier": rank["tier"],
                            "division": rank["division"],
                            "leaguePoints": rank["leaguePoints"],
                        }

            # Check if match already exists in database
            collection = client["rank-crawler"]["matches"]
            match = collection.find_one({"metadata.matchId": match_data["metadata"]["matchId"]})
            if match:
                print(f"    Match {match_id} already exists in database")
                continue

            # Add match to database
            collection.insert_one(match_data)
            print(f"    Successfully added match {match_id} to database")

        # Increase start by count
        start += count



def add_summoner(summoner_name, platform):
    """
    Get the summoner data from the Riot API and add enrich it with the rank data from the database
    """
    print(f"Trying to add {summoner_name} to database")
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
    response = requests.get(url)
    summoner_data = response.json()

    collection = client["rank-crawler"]["summoners"]

    # Check if summoner already exists in database
    summoner = collection.find_one({"id": summoner_data["id"]})
    if summoner:
        print(f"    {summoner_name} already exists in database")
        return
    
    #Add platform to summoner_data
    summoner_data["platform"] = platform

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

    # Add summoner to database
    collection.insert_one(summoner_data)
    print(f"Successfully added {summoner_name} to database")




def main():
    """
    if len(sys.argv) != 3:
        print('Usage: python add_summoner.py "<summoner_name>" "<platform>"')
        sys.exit(1)

    
    summoner_name = sys.argv[1]
    platform = sys.argv[2]
    """
    summoner_name = "G5 Easy"
    platform = "euw1"

    add_summoner(summoner_name, platform)
    save_matches(summoner_name, platform)


if __name__ == "__main__":
    main()