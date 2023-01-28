import enum

class Region(enum.Enum):
    BR1 = 0,
    EUN1 = 1,
    EUW1 = 2,
    JP1 = 3,
    KR = 4,
    LA1 = 5,
    LA2 = 6,
    NA1 = 7,
    OC1 = 8,
    TR1 = 9,
    RU = 10,
    RH2 = 11,
    SG2 = 12,
    TH2 = 13,
    TW2 = 14,
    VN2 = 15

class GameMode(enum.Enum):
    CLASSIC = 0,
    ODIN = 1,
    ARAM = 2,
    TUTORIAL = 3,
    URF = 4,
    DOOMBOTSTEEMO = 5,
    ONEFORALL = 6,
    ASCENSION = 7,
    FIRSTBLOOD = 8,
    KINGPORO = 9,
    SIEGE = 10,
    ASSASSINATE = 11,
    ARSR = 12,
    DARKSTAR = 13,
    STARGUARDIAN = 14,
    PROJECT = 15,
    GAMEMODEX = 16,
    ODYSSEY = 17,
    NEXUSBLITZ = 18,
    ULTBOOK = 19

class GameType(enum.Enum):
    CUSTOM_GAME = 0,
    MATCHED_GAME = 1,
    TUTORIAL_GAME = 2

class PerkPossition(enum.Enum):
    PRIMARY = 0,
    SECONDARY = 1

class ObjectiveName(enum.Enum):
    baron = 0,
    champion = 1,
    dragon = 2,
    inhibitor = 3,
    riftHerald = 4,
    tower = 5