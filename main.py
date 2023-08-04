import sqlite3
import requests
import time
import os
from dotenv import load_dotenv
import schedule


load_dotenv()
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

SUMMONERS = [
    {
        "id": "Esssl3ai9Cyz-n3-QkcXtgUrkG7eR2rWOYcbbymH2wptaz8", # G5 Easy
        "puuid": "eL5FT_-iar7RRvNBDsj5arXPUTWdkfrJTFhReKgDHNBizr37dHJf9ruCdfrJZmWpamye3L-W67aShw"
    },
    {
        "id": "4E83JFYB1u3IXauxJEsBTuVef3MdiJhGCjoeI1Oum0sTVQk0", # WeingottBachus
        "puuid": "DD9JnerCOP2Ag49m3HWlgcWuiPYpGp9Mpldd5UPuo57VNKguh3_eLySKBQ90uP8hkJlFBOP7x24CDQ"
    },
    {
        "id": "9mMuO06QQxEyFY-pmoxQgEidD-_vBgX_TluPPUKBfG5Vfkw", # Shinzoυ
        "puuid": "kI861zvO4_5X6gfpbcYTqSh6N4miWNffv6qqS29PulV3nWy9wOchnO2lfRMDKydxzwWzUMh2MWGAIg"
    },
    {
        "id": "OToOysaeJ_zY6ZnhCHLwBRPxGcpKkbvEOkM7ia2Y4KWjmmxQ", # kiting femboys
        "puuid": "xLoyhMEWCKwyxLY9-aovS3WxuFwaZk3MAwCWeDV0lhE-Av_NiV0t-_Z4PYdY8BV-aYgDA9wod8xX2Q"
    },
    {
        "id": "wCslB5tO7mJZt_nWQPy-tf-H_0Wglz_q4d4K76L5EPHJs_XvdqzdSLGeZg", # PrinzessinBubbIe
        "puuid": "MujvQi2r1ukKYB0We1WQj1g9zuDF8L3mX6y5xGl59QoUQCvuuT4OFahVIuH8Bbq-6jgQ8gHjKuJ10g"
    },
    {
        "id": "80Eyjcf06d_aZSnrOXR85GWJKR7K_9m63XYhZVm-MBTlunhC", # Zukyami
        "puuid": "8EnGr9cgFf5vxShBrwLpToRH_202wXcDwSsE6X_iXkpaQR0o4uSXHVBXKGRlp-BSvYrBwMlHtEXO7g"
    },
    {
        "id": "JGx-65ycqCkFQ4EcFU-8byy0Iex9DeLQahV24tqfL3i1IKGb", # qyiugweqyeh
        "puuid": "J2YqSWNftal_UKOV9TK7Wb2Z8zWOcdUwvMYqowwMreVqqjaPITvxaLoC_qe1l8x7kNiRuqnJFujFMQ"
    },
    {
        "id": "5r6plhza1fMe20t8Cq3e-9ACtSiHNzIiiGIsPPdfeUkATYA", # tiger woods 1
        "puuid": "DciWwrGbDNmMX48dOmyc2U7to5HJCJAagc1tZwPh6cWs4Frxdps-_vBHEk5NDE9QkvzQJRnjj06ygQ"
    },
    {
        "id": "5r6plhza1fMe20t8Cq3e-9ACtSiHNzIiiGIsPPdfeUkATYA", # dying alive
        "puuid": "DciWwrGbDNmMX48dOmyc2U7to5HJCJAagc1tZwPh6cWs4Frxdps-_vBHEk5NDE9QkvzQJRnjj06ygQ"
    }

]

def save_rank(queue, summoner_puuid, tier, rank, lp):
    if queue == "RANKED_SOLO_5x5":
        tabel = "rank_solo"
    elif queue == "RANKED_FLEX_SR":
        tabel = "rank_flex"
    else:
        return

    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # Check if this is the first time we are saving a rank for this summoner
    c.execute(f"SELECT * FROM {tabel} WHERE puuid = '{summoner_puuid}'")
    if c.fetchone() is not None:
        # Check if the rank has changed since the last time we checked
        c.execute(f"SELECT * FROM {tabel} WHERE puuid = '{summoner_puuid}' ORDER BY timestamp DESC LIMIT 1")
        last_rank = c.fetchone()
        if last_rank is not None:
            if last_rank[2] == tier and last_rank[3] == rank and last_rank[4] == lp:
                return

    # Save the rank
    c.execute(f"INSERT INTO {tabel} VALUES (?, ?, ?, ?, ?)", (summoner_puuid, int(time.time()), tier, rank, lp))
    conn.commit()
    conn.close()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully saved rank for {summoner_puuid}")

def check_ranks():
    print()
    for summoner in SUMMONERS:
        summoner_id = summoner["id"]
        summoner_puuid = summoner["puuid"]
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking rank for {summoner_puuid}")
        url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={RIOT_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for queue in data:
                if queue["queueType"] == "RANKED_SOLO_5x5" or queue["queueType"] == "RANKED_FLEX_SR":
                    tier = queue["tier"]
                    rank = queue["rank"]
                    lp = queue["leaguePoints"]
                    queue_type = queue["queueType"]
                    save_rank(queue_type, summoner_puuid, tier, rank, lp)
        else:
            print(f"Error getting rank for {summoner_puuid}")
            print(response.text)

def main():
    check_ranks()


if __name__ == "__main__":
    for minute in range(0, 60, 5):
        schedule.every().hour.at(f":{minute:02d}").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
