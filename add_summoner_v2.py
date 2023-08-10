import logging
import os
import argparse
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from riotwatcher import LolWatcher, ApiError


# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Static variables
REGIONS = ['br1', 'eun1', 'euw1', 'jp1', 'kr', 'la1', 'la2', 'na1', 'oc1', 'tr1', 'ru', 'ph2', 'sg2', 'th2', 'tw2', 'vn2']

# Configure logging
logging.basicConfig(filename='logs/add_summoner_v2.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


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


def save_summoner_to_database(client, summoner_name, platform, lol_watcher):
    '''Saves a summoner to the database.'''
    summoner_collection = client['rank-crawler']['summoners']

    # Check if summoner is already in database
    existing_summoner = summoner_collection.find_one({'name': summoner_name, 'platform': platform})
    if existing_summoner:
        logging.info('Summoner already in database!')
        return

    try:
        # Get summoner data
        summoner_data = lol_watcher.summoner.by_name(platform, summoner_name)
        summoner_data['platform'] = platform

        # Get the league data
        league_entries = lol_watcher.league.by_summoner(platform, summoner_data['id'])

        # Remove unnecessary fields from league data
        for league_entry in league_entries:
            del league_entry['summonerId']
            del league_entry['summonerName']

        # Merge the league data into the summoner data
        summoner_data['league_entries'] = league_entries

        # Save summoner to database
        summoner_collection.insert_one(summoner_data)
        logging.info(f'Saved summoner {summoner_name} from platform {platform} to database.')
    except ApiError as api_error:
        logging.error(f'API Error: {api_error}')


def main():
    # Get summoner name and platform from command line arguments
    parser = argparse.ArgumentParser(description='Add a summoner to the database.')
    parser.add_argument('-name', type=str, required=True, help='The summoner name.')
    parser.add_argument('-region', type=str, required=True, help='The platform.', choices=REGIONS)
    args = parser.parse_args()

    # Set up MongoDB connection
    client = setup_mongodb_connection(DB_USER, DB_PASSWORD)

    # Set up RiotWatcher
    lol_watcher = LolWatcher(RIOT_API_KEY)

    # Save summoner to database
    save_summoner_to_database(client, args.name, args.region, lol_watcher)

    # Close MongoDB connection
    client.close()


if __name__ == '__main__':
    main()
