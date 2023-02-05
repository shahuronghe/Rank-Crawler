from sqlalchemy import Table, Column, ForeignKey, create_engine
from sqlalchemy import BIGINT, INTEGER, SMALLINT
from sqlalchemy import TEXT, VARCHAR, CHAR
from sqlalchemy import BOOLEAN, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from assets.enums import platforms, objectives, ranks, tiers

class Base(DeclarativeBase):
    pass

class Summoner(Base):
    __tablename__ = 'summoners'
    puuid = Column(VARCHAR(78), primary_key=True)
    id = Column(VARCHAR(63), nullable=False)
    name = Column(VARCHAR(16), nullable=False)
    profileIconId = Column(INTEGER, nullable=False)
    revisionDate = Column(BIGINT, nullable=False)
    summonerLevel = Column(INTEGER, nullable=False)

    matches = relationship("Participant", back_populates="summoner")

    def __repr__(self):
        return f"{self.name} ({self.puuid})"


class Match(Base):
    __tablename__ = 'matches'
    gameId = Column(BIGINT, primary_key=True)
    platformId = Column(Enum(platforms), primary_key=True, nullable=False)
    gameCreation = Column(BIGINT, nullable=False)
    gameDuration = Column(INTEGER, nullable=False)
    gameEndTimestamp = Column(BIGINT, nullable=False)
    gameMode = Column(TEXT, nullable=False)
    gameStartTimestamp = Column(BIGINT, nullable=False)
    gameType = Column(TEXT, nullable=False)
    gameVersion = Column(TEXT, nullable=False)
    mapId = Column(INTEGER, nullable=False)
    queueId = Column(INTEGER, nullable=False)
    tournamentCode = Column(TEXT, nullable=False)

    participants = relationship("Participant", back_populates="match")
    teams = relationship("Team", back_populates="match")

    def __repr__(self):
        return f"{self.gameId} ({self.platformId})"
    

class Participant(Base):
    __tablename__ = 'participants'
    summoner_puuid = Column(VARCHAR(78), ForeignKey("summoners.puuid"), primary_key=True)
    match_gameId = Column(BIGINT, ForeignKey("matches.gameId"), primary_key=True)
    match_platformId = Column(Enum(platforms), ForeignKey("matches.platformId"), primary_key=True)
    teamId = Column(INTEGER, nullable=False)
    summonerName = Column(VARCHAR(16), nullable=False)
    championName = Column(VARCHAR(16), nullable=False)
    championId = Column(INTEGER, nullable=False)
    kills = Column(INTEGER, nullable=False)
    deaths = Column(INTEGER, nullable=False)
    assists = Column(INTEGER, nullable=False)
    item0 = Column(INTEGER, nullable=False)	
    item1 = Column(INTEGER, nullable=False)
    item2 = Column(INTEGER, nullable=False)
    item3 = Column(INTEGER, nullable=False)
    item4 = Column(INTEGER, nullable=False)
    item5 = Column(INTEGER, nullable=False)
    item6 = Column(INTEGER, nullable=False)
    summoner1Id = Column(INTEGER, nullable=False)
    summoner2Id = Column(INTEGER, nullable=False)
    primaryPerkStyle = Column(INTEGER, nullable=False)
    secondaryPerkStyle = Column(INTEGER, nullable=False)
    primaryPerk0Id = Column(INTEGER, nullable=False)
    primaryPerk1Id = Column(INTEGER, nullable=False)
    primaryPerk2Id = Column(INTEGER, nullable=False)
    primaryPerk3Id = Column(INTEGER, nullable=False)
    secondaryPerk0Id = Column(INTEGER, nullable=False)
    secondaryPerk1Id = Column(INTEGER, nullable=False)
    statPerk0 = Column(INTEGER, nullable=False)
    statPerk1 = Column(INTEGER, nullable=False)
    statPerk2 = Column(INTEGER, nullable=False)
    bannedChampionId = Column(INTEGER, nullable=False)
    win = Column(BOOLEAN, nullable=False)
    rank = Column(Enum(ranks), nullable=False)
    tier = Column(Enum(tiers), nullable=False)
    leaguePoints = Column(INTEGER, nullable=False)

    summoner = relationship("Summoner", back_populates="matches")
    match = relationship("Match", back_populates="participants")
    teams = relationship("Team", back_populates="match")

    def __repr__(self):
        return f"{self.summonerName} ({self.summoner_puuid})"
    


class Team(Base):
    __tablename__ = 'teams'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    match_gameId = Column(BIGINT, ForeignKey("matches.gameId"))
    match_platformId = Column(Enum(platforms), ForeignKey("matches.platformId"))
    teamId = Column(INTEGER, nullable=False)
    win = Column(BOOLEAN, nullable=False)

    match = relationship("Match", back_populates="teams")
    objectives = relationship("Objective", back_populates="team")

    def __repr__(self):
        return f"{self.teamId} ({self.match_gameId})"


class Objective(Base):
    __tablename__ = 'objectives'
    team_id = Column(INTEGER, ForeignKey("teams.id"), primary_key=True)
    objectiveName = Column(Enum(objectives))
    first = Column(BOOLEAN, nullable=False)
    kills = Column(INTEGER, nullable=False)

    team = relationship("Team", back_populates="objectives")

    def __repr__(self):
        return f"{self.objectiveName} ({self.team_id})"


# Create the empty tables
engine = create_engine('sqlite:///data.db')
Base.metadata.create_all(engine)