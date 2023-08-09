platform2regions = {
    "br1": "americas",
    "eun1": "europe",
    "euw1": "europe",
    "jp1": "asia",
    "kr": "asia",
    "la1": "americas",
    "la2": "americas",
    "na1": "americas",
    "oc1": "sea",
    "tr1": "europe",
    "ru": "europe",
    "ph2": "sea",
    "sg2": "sea",
    "th2": "sea",
    "tw2": "sea",
    "vn2": "sea",
}

platform2cass_regions = {
    "br1": "BR",
    "eun1": "EUNE",
    "euw1": "EUW",
    "jp1": "JP",
    "kr": "KR",
    "la1": "LAN",
    "la2": "LAS",
    "na1": "NA",
    "oc1": "OCE",
    "tr1": "TR",
    "ru": "RU",
    "ph2": "PH",
    "sg2": "SG",
    "th2": "TH",
    "tw2": "TW",
    "vn2": "VN",
}


def platform_to_region(plattform: str) -> str:
    '''Return the region correspondent to a given platform'''
    return platform2regions[plattform]


def platform_to_cass_region(plattform: str) -> str:
    '''Return the region correspondent to a given platform'''
    return platform2cass_regions[plattform]
