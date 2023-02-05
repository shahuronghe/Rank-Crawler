import enum

class platforms(enum.Enum):
    BR1 = 0
    EUN1 = 1
    EUW1 = 2
    JP1 = 3
    KR = 4
    LA1 = 5
    LA2 = 6
    NA1 = 7
    OC1 = 8
    TR1 = 9
    RU = 10
    PH2 = 11
    SG2 = 12
    TH2 = 13
    TW2 = 14
    VN2 = 15

class objectives(enum.Enum):
    baron = 0
    champion = 1
    dragon = 2
    inhibitor = 3
    riftHerald = 4
    tower = 5

class ranks(enum.Enum):
    I = 0
    II = 1
    III = 2
    IV = 3
    V = 4

class tiers(enum.Enum):
    CHALLENGER = 0
    GRANDMASTER = 1
    MASTER = 2
    DIAMOND = 3
    PLATINUM = 4
    GOLD = 5
    SILVER = 6
    BRONZE = 7
    IRON = 8