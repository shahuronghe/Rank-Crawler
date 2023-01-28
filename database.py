from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, CHAR, VARCHAR, Enum
from sqlalchemy.ext.declarative import declarative_base
from assets.enums import Region, GameMode, GameType, PerkPossition, ObjectiveName

Base = declarative_base()


class Summoner(Base):
    __tablename__ = 'summoners'
    puuid = Column('puuid', CHAR(78), primary_key=True)
    id = Column('id', CHAR(63), nullable=False)
    name = Column('name', String(16), nullable=False)
    profileIconId = Column('profileIconId', Integer, nullable=False)
    revisionDate = Column('revisionDate', Integer, nullable=False)
    summonerLevel = Column('summonerLevel', Integer, nullable=False)
    region = Column('region', Enum(Region), nullable=False)

    def __init__(self, puuid, id, name, profileIconId, revisionDate, summonerLevel, region):
        self.puuid = puuid
        self.id = id
        self.name = name
        self.profileIconId = profileIconId
        self.revisionDate = revisionDate
        self.summonerLevel = summonerLevel
        self.region = region


class Match(Base):
    __tablename__ = 'matches'
    gameId = Column('gameId', Integer, primary_key=True)
    platformId = Column('platformId', Enum(Region), primary_key=True)
    gameCreation = Column('gameCreation', Integer, nullable=False)
    gameDuration = Column('gameDuration', Integer, nullable=False)
    gameEndTimestamp = Column('gameEndTimestamp', Integer, nullable=False)
    gameMode = Column('gameMode', Enum(GameMode), nullable=False)
    gameName = Column('gameName', String(256), nullable=False)
    gameStartTimestamp = Column('gameStartTimestamp', Integer, nullable=False)
    gameType = Column('gameType', Enum(GameType), nullable=False)
    gameVersion = Column('gameVersion', String(256), nullable=False)
    mapId = Column('mapId', Integer, nullable=False)
    queueId = Column('queueId', Integer, nullable=False)
    tournamentCode = Column('tournamentCode', String(256), nullable=False)

    def __init__(
        self,
        gameId,
        platformId,
        gameCreation,
        gameDuration,
        gameEndTimestamp,
        gameMode,
        gameName,
        gameStartTimestamp,
        gameType,
        gameVersion,
        mapId,
        queueId,
        tournamentCode
        ):
        self.gameId = gameId
        self.platformId = platformId
        self.gameCreation = gameCreation
        self.gameDuration = gameDuration
        self.gameEndTimestamp = gameEndTimestamp
        self.gameMode = gameMode
        self.gameName = gameName
        self.gameStartTimestamp = gameStartTimestamp
        self.gameType = gameType
        self.gameVersion = gameVersion
        self.mapId = mapId
        self.queueId = queueId
        self.tournamentCode = tournamentCode


class Participant(Base):
    __tablename__ = 'participants'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    summoner_puuid = Column('summoner.puuid', CHAR(78), nullable=False)
    match_gameId = Column('match.gameId', Integer, nullable=False)
    match_platformId = Column('match.platformId', Enum(Region), nullable=False)
    summonerName = Column('summonerName', VARCHAR(16), nullable=False)
    championName = Column('championName', VARCHAR(16), nullable=False)
    championId = Column('championId', Integer, nullable=False)
    kills = Column('kills', Integer, nullable=False)
    deaths = Column('deaths', Integer, nullable=False)
    assists = Column('assists', Integer, nullable=False)
    item0 = Column('item0', Integer, nullable=False)
    item1 = Column('item1', Integer, nullable=False)
    item2 = Column('item2', Integer, nullable=False)
    item3 = Column('item3', Integer, nullable=False)
    item4 = Column('item4', Integer, nullable=False)
    item5 = Column('item5', Integer, nullable=False)
    item6 = Column('item6', Integer, nullable=False)
    summoner1Id = Column('summoner1Id', Integer, nullable=False)
    summoner2Id = Column('summoner2Id', Integer, nullable=False)
    win = Column('win', Boolean, nullable=False)

    def __init__(
        self,
        summoner_puuid,
        match_gameId,
        match_platformId,
        summonerName,
        championName,
        championId,
        kills,
        deaths,
        assists,
        item0,
        item1,
        item2,
        item3,
        item4,
        item5,
        item6,
        summoner1Id,
        summoner2Id,
        win
        ):
        self.summoner_puuid = summoner_puuid
        self.match_gameId = match_gameId
        self.match_platformId = match_platformId
        self.summonerName = summonerName
        self.championName = championName
        self.championId = championId
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.item0 = item0
        self.item1 = item1
        self.item2 = item2
        self.item3 = item3
        self.item4 = item4
        self.item5 = item5
        self.item6 = item6
        self.summoner1Id = summoner1Id
        self.summoner2Id = summoner2Id
        self.win = win


class Perks_Participants(Base):
    __tablename__ = 'perks_participants'
    participants_id = Column('participants.id', Integer)
    statPerks_id = Column('statPerks.id', Integer)
    styles_id = Column('styles.id', Integer)

    def __init__(self, participants_id, statPerks_id, styles_id):
        self.participants_id = participants_id
        self.statPerks_id = statPerks_id
        self.styles_id = styles_id


class statPerks(Base):
    __tablename__ = 'statPerks'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    defense = Column('defense', Integer, nullable=False)
    flex = Column('flex', Integer, nullable=False)
    offense = Column('offense', Integer, nullable=False)

    def __init__(self, participants_id, defense, flex, offense):
        self.participants_id = participants_id
        self.defense = defense
        self.flex = flex
        self.offense = offense


class styles(Base):
    __tablename__ = 'styles'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    description = Column('description', String(256), nullable=False)
    position = Column('position', Enum(PerkPossition), nullable=False)
    description = Column('description', String(256), nullable=False)
    perk = Column('perk', Integer, nullable=False)
    var1 = Column('var1', Integer, nullable=False)
    var2 = Column('var2', Integer, nullable=False)
    var3 = Column('var3', Integer, nullable=False)

    def __init__(self, participants_id, description, position, perk, var1, var2, var3):
        self.participants_id = participants_id
        self.description = description
        self.position = position
        self.perk = perk
        self.var1 = var1
        self.var2 = var2
        self.var3 = var3


class Team(Base):
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    match_gameId = Column('match.gameId', Integer, nullable=False)
    match_platformId = Column('match.platformId', Enum(Region), nullable=False)
    teamId = Column('teamId', Integer, nullable=False)
    win = Column('win', Boolean, nullable=False)

    def __init__(self, match_gameId, match_platformId, teamId, win):
        self.match_gameId = match_gameId
        self.match_platformId = match_platformId
        self.teamId = teamId
        self.win = win


class Ban(Base):
    __tablename__ = 'bans'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    team_id = Column('team.id', Integer, nullable=False)
    championId = Column('championId', Integer, nullable=False)
    pickTurn = Column('pickTurn', Integer, nullable=False)

    def __init__(self, team_id, championId, pickTurn):
        self.team_id = team_id
        self.championId = championId
        self.pickTurn = pickTurn


class Objective(Base):
    __tablename__ = 'objectives'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    team_id = Column('team.id', Integer, nullable=False)
    objectiveName = Column('objectiveName', Enum(ObjectiveName), nullable=False)
    first = Column('first', Boolean, nullable=False)
    kills = Column('kills', Integer, nullable=False)

    def __init__(self, team_id, objectiveName, first, kills):
        self.team_id = team_id
        self.objectiveName = objectiveName
        self.first = first
        self.kills = kills