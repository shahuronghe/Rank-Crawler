import logging
import time
import os
import schedule
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from riotwatcher import LolWatcher, ApiError

'''
This script updates summoner and league data for registered summoners in a MongoDB database using the Riot Games API.
It retrieves summoner information and league entries for each summoner, compares the data with the existing records in the database,
and updates the records if any changes are detected. The script uses the RiotWatcher library for interacting with the Riot Games API,
and it schedules periodic updates for all summoners at specified intervals.
'''

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Configure logging
logging.basicConfig(filename='logs/main.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger('riotwatcher').setLevel(logging.ERROR)

def setup_mongodb_connection(db_user, db_password):
    '''Set up MongoDB connection.'''
    uri = f'mongodb+srv://{db_user}:{db_password}@cluster0.cgxkcwy.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Test MongoDB connection
    try:
        client.admin.command('ping')
        logging.info('Pinged MongoDB!')
    except Exception as e:
        logging.error(f'MongoDB ping failed: {e}')

    return client


def update_all_summoners(client, lol_watcher):
    '''Update all summoners in the database.'''
    summoner_collection = client['rank-crawler']['summoners']

    # Get all summoners from the database
    summoners = summoner_collection.find()
    for summoner in summoners:
        # Get data
        try:
            summoner_data = lol_watcher.summoner.by_name(summoner['platform'], summoner['name'])
            league_entries = lol_watcher.league.by_summoner(summoner['platform'], summoner_data['id'])
        except ApiError as api_error:
            logging.error(f'API Error: {api_error}')
            continue
        
        # Remove unnecessary fields from league_entries
        for league_entry in league_entries:
            del league_entry['summonerId']
            del league_entry['summonerName']

        # Enrich summoner data
        summoner_data['platform'] = summoner['platform']
        summoner_data['league_entries'] = league_entries

        # Check if summoner data has changed
        summoner_copy = summoner.copy()
        del summoner_copy['_id']
        if summoner_data == summoner_copy:
            logging.info(f'Summoner {summoner_copy["name"]} has not changed')
            continue

        # Show what exactly has changed
        change = False
        for key in summoner_data:
            if summoner_data[key] != summoner_copy[key]:
                if key == "league_entries" and [i for i in summoner_data[key] if i not in summoner_copy[key]] == []:
                    break
                logging.info(f'{key} has changed from {summoner_copy[key]} to {summoner_data[key]}')
                change = True
                break

        # Update summoner data
        if change:
            summoner_collection.update_one({'_id': summoner['_id']}, {'$set': summoner_data})
            logging.info(f'Updated summoner {summoner["name"]}')

    logging.info('Finished updating all summoners!')


def main():
    # Set up MongoDB connection
    client = setup_mongodb_connection(DB_USER, DB_PASSWORD)

    # Set up Riot API connection
    lol_watcher = LolWatcher(RIOT_API_KEY)

    # Update all summoners
    update_all_summoners(client, lol_watcher)

    # Update all summoners every 5 minutes
    schedule.every(5).minutes.at(':00').do(update_all_summoners, client, lol_watcher)

    # Run scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
