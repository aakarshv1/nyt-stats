import requests
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as soup 
import csv
import configparser
import asyncio
import aiohttp
import sys

#https://github.com/mattdodge/nyt-crossword-stats/blob/master/fetch_puzzle_stats.py
#https://github.com/kyledeanreinford/NYT_Mini_Leaderboard_Scraper

if len(sys.argv) < 3:
    raise ValueError("Please input both a username and password")

user = sys.argv[1]
password = sys.argv[2]


# print(user)
# print(password)

def login(username, password):
    """ Return the NYT-S cookie after logging in """
    login_resp = requests.post(
        'https://myaccount.nytimes.com/svc/ios/v2/login',
        data={
            'login': username,
            'password': password,
        },
        headers={
            'User-Agent': 'Crosswords/20191213190708 CFNetwork/1128.0.1 Darwin/19.6.0',
            'client_id': 'ios.crosswords',
        },
    )
    login_resp.raise_for_status()
    for cookie in login_resp.json()['data']['cookies']:
        if cookie['name'] == 'NYT-S':
            return cookie['cipheredValue']
    raise ValueError('NYT-S cookie not found')

config = configparser.ConfigParser()
config.read('config.ini')
api_key = login(user, password)
API_ROOT = 'https://nyt-games-prd.appspot.com/svc/crosswords'
PUZZLE_INFO = API_ROOT + '/v3/undefined/puzzles.json?publish_type=mini&date_start={start}&date_end={end}'
SOLVE_INFO = API_ROOT + '/v6/game/{game_id}.json'
#players = ['Aak', 'Bobo22', 'yjsi', 'Pankek']

def get_quarter_pairs():
    today = datetime.now()
    start_date = today - timedelta(days=365 * 4)  # Set the start date 4 years back

    quarter_pairs = []
    current_start_date = start_date
    while current_start_date < today:
        end_date = current_start_date + timedelta(days=89)  # Set the end date as 89 days (approximately 3 months) after the start date
        quarter_pairs.append([current_start_date.date().isoformat(), end_date.date().isoformat()])

        current_start_date += timedelta(days=90)  # Move to the next quarter start date

    quarter_pairs[-1][1] = (today + timedelta(days=1)).date().isoformat()

    return quarter_pairs

def getMiniStat(id):
    puzzle_resp = requests.get(
        SOLVE_INFO.format(game_id=id),
        cookies={
            'NYT-S': api_key,
        },
    )
    return puzzle_resp.json()

async def asyncGMS(session, id):
    MINI_STAT_ENDPOINT = SOLVE_INFO.format(game_id=id)
    headers = {
        "Cookie": f"NYT-S={api_key}"
    }
    async with session.get(MINI_STAT_ENDPOINT, headers=headers) as response:
        data = await response.json()
        return data['calcs']['secondsSpentSolving']



async def getMiniInfo(session, start_date: str, end_date: str):
    headers = {
        "Cookie": f"NYT-S={api_key}"
    }
    async with session.get(
            PUZZLE_INFO.format(start=start_date, end=end_date),
            headers=headers
        ) as response:
        return json.loads(await response.text())

async def getIds(incSat=True):
    dates = get_quarter_pairs()
    ids = []
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = []
        for pair in dates:
            task = asyncio.create_task(getMiniInfo(session, pair[0], pair[1]))
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        for resp in responses:
            for dict in resp['results']:
                if dict['solved']:
                    ids.append(dict['puzzle_id'])
        
    return ids



async def asyncGST():
    ids = await getIds()
    times = []
    # for id in ids:
    #     time = getMiniStat(id)['calcs']['secondsSpentSolving']
    #     print(time)
    #     times.append(time)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = [asyncGMS(session, puzzle_id) for puzzle_id in ids]
        times = await asyncio.gather(*tasks)

    return times

def getSolveTimes():
    times = asyncio.run(asyncGST())
    print(times)

    plt.hist(times, bins=200)
    plt.title(f"Mini Crossword Stats (Last 4 Years)")
    plt.xlabel("Solve Time")
    plt.ylabel("Counts")
    plt.savefig("results.png")
                                                                        


# Main execution
if __name__ == "__main__":
    #stats = get_mini_crossword_stats()
    #getStats("2021-06-01")
    #get_mini_times(api_key, "test.csv")
    #print(login("aakarshvermani@gmail.com", "Chemistry12@"))
    #test()
    #print(get_quarter_pairs())
    getSolveTimes()
    #print(config.get('NYT Password', 'PASSWORD'))
    

#https:\u002F\u002Fmyaccount.nytimes.com\u002Fauth\u002Fenter-email?redirect_uri=https%3A%2F%2Fwww.nytimes.com%2Fpuzzles%2Fleaderboards&response_type=cookie&client_id=games&application=crosswords&asset=leaderboard","register":"https:\u002F\u002Fmyaccount.nytimes.com\u002Fauth\u002Fregister?redirect_uri=https%3A%2F%2Fwww.nytimes.com%2Fpuzzles%2Fleaderboards&response_type=cookie&client_id=games&application=crosswords&asset=leaderboard","printDate":"2023-06-29","puzzleLink":"\u002Fcrosswords\u002Fgame\u002Fmini\u002F2023\u002F06\u002F29
