from riotwatcher import LolWatcher, ApiError
import os
from models import Summoner, Match, Participant, Team, Objective
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

API_KEY = os.environ.get('RIOT_API_KEY')
lol_watcher = LolWatcher(API_KEY)

def get_summoner(name, region):
    summoner = lol_watcher.summoner.by_name(region, name)
    return summoner

def get_match_history(summoner, region):
    match_history = lol_watcher.match.matchlist_by_puuid(region, summoner['puuid'])
    return match_history

def get_match(match_id, region):
    match = lol_watcher.match.by_id(region, match_id)
    return match

def save_summoner_to_db(summoner):
    engine = create_engine('sqlite:///data.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    new_summoner = Summoner(puuid=summoner['puuid'], id=summoner['id'], name=summoner['name'], profileIconId=summoner['profileIconId'], revisionDate=summoner['revisionDate'], summonerLevel=summoner['summonerLevel'])
    session.add(new_summoner)
    session.commit()