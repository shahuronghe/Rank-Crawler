import os

from pymongo import MongoClient
from riotwatcher import ApiError, LolWatcher


class RankCrawler:
    def __init__(self, api_key, mongodb_pw):
        self.watcher = LolWatcher(api_key)
        self.mongodb_pw = mongodb_pw

        self.RANKED_SOLO_5x5 = 420
        self.RANKED_TEAM_5x5 = 440

        self.CONNECTION_STRING = f'mongodb+srv://user:{mongodb_pw}@rank-crawler.kvodu7l.mongodb.net/?retryWrites=true&w=majority'
        self.client = MongoClient(self.CONNECTION_STRING)
        self.rank_crawler_db = self.client['rank-crawler']

    def get_last_match_id(self, summoner_region, summoner_puuid):
        my_matches = self.watcher.match.matchlist_by_puuid(summoner_region, summoner_puuid)
        return my_matches[0]

    def add_summoner_to_db(self, summoner_data):
        self.rank_crawler_db.summoner.insert_one(summoner_data)

    def get_summoner_rank(self, summoner_region, summoner_id, league_type):
        # league_type should be either 'RANKED_SOLO_5x5' or 'RANKED_TEAM_5x5'
        leagues = self.watcher.league.by_summoner(summoner_region, summoner_id)
        for league in leagues:
            if league["queueType"] == league_type:
                return league
        return None


    def add_last_match_to_db(self, last_match):
        if last_match['info']['queueId'] == self.RANKED_SOLO_5x5 or last_match['info']['queueId'] == self.RANKED_TEAM_5x5:
            for participant in last_match['info']['participants']:
                summoner = self.rank_crawler_db.summoner.find_one({'puuid': participant['puuid']})
                if summoner:
                    if last_match['info']['queueId'] == self.RANKED_SOLO_5x5:
                        summoner_region = summoner['region']
                        summoner_id = summoner['id']
                        league = self.get_summoner_rank(summoner_region, summoner_id, 'RANKED_SOLO_5x5')
                    if last_match['info']['queueId'] == self.RANKED_TEAM_5x5:
                        summoner_region = summoner['region']
                        summoner_id = summoner['id']
                        league = self.get_summoner_rank(summoner_region, summoner_id, 'RANKED_TEAM_5x5')
                    if league:
                        participant['league'] = {
                            'tier': league['tier'],
                            'rank': league['rank'],
                            'leaguePoints': league['leaguePoints'],
                            'wins': league['wins'],
                            'losses': league['losses'],
                            'veteran': league['veteran'],
                            'inactive': league['inactive'],
                            'freshBlood': league['freshBlood'],
                            'hotStreak': league['hotStreak']
                        }
        self.rank_crawler_db.match.insert_one(last_match)

    def get_summoner_data(self, summoner_name, summoner_region):
        try:
            summoner = self.watcher.summoner.by_name(summoner_region, summoner_name)
        except ApiError as err:
            if err.response.status_code == 404:
                print('Summoner not found. Please try again.')
                return None
            else:
                raise
        last_match_id = self.get_last_match_id(summoner_region, summoner['puuid'])

        existing_summoner = self.rank_crawler_db.summoner.find_one({'puuid': summoner['puuid']})

        if existing_summoner:
            print(f'Summoner {summoner_name} already exists in the database.')
            return None

        summoner_data = summoner
        summoner_data['region'] = summoner_region.upper()
        summoner_data['matches'] = []
        summoner_data['matches'].insert(0, last_match_id)

        return summoner_data

    def add_summoner(self, summoner_name, summoner_region):
        summoner_data = self.get_summoner_data(summoner_name, summoner_region)
        if summoner_data:
            self.add_summoner_to_db(summoner_data)

            last_match = self.watcher.match.by_id(summoner_region, summoner_data['matches'][0])
            self.add_last_match_to_db(last_match)

if __name__ == '__main__':
    api_key = os.getenv('RIOT_API_KEY')
    mongodb_pw = os.getenv('MONGODB_PW')
    rank_crawler = RankCrawler(api_key, mongodb_pw)
    PLATFORM_LIST = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'TR1', 'RU', 'PH2', 'SG2', 'TH2', 'TW2', 'VN2']
    
    summoner_name_input = input('Enter summoner name: ')
    if summoner_name_input == '':
        print('Please enter a summoner name.')
        exit()
    summoner_region_input = input('Enter summoner region: ')
    if summoner_region_input == '':
        print('Please enter a summoner region.')
        exit()
    if summoner_region_input not in PLATFORM_LIST:
        print('Please enter a valid region.')
        exit()
    rank_crawler.add_summoner(summoner_name_input, summoner_region_input)