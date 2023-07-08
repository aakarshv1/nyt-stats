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

#api_key = login(user, password)
API_ROOT = 'https://nyt-games-prd.appspot.com/svc/crosswords'
PUZZLE_INFO = API_ROOT + '/v3/undefined/puzzles.json?publish_type=mini&date_start={start}&date_end={end}'
SOLVE_INFO = API_ROOT + '/v6/game/{game_id}.json'

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



async def asyncGMS(session, key, id):
    MINI_STAT_ENDPOINT = SOLVE_INFO.format(game_id=id)
    headers = {
        "Cookie": f"NYT-S={key}"
    }
    async with session.get(MINI_STAT_ENDPOINT, headers=headers) as response:
        data = await response.json()
        return data['calcs']['secondsSpentSolving']



async def getMiniInfo(session, key, start_date: str, end_date: str):
    headers = {
        "Cookie": f"NYT-S={key}"
    }
    async with session.get(
            PUZZLE_INFO.format(start=start_date, end=end_date),
            headers=headers
        ) as response:
        return json.loads(await response.text())

async def getIds(key, incSat=True):
    dates = get_quarter_pairs()
    ids = []
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = []
        for pair in dates:
            task = asyncio.create_task(getMiniInfo(session, key, pair[0], pair[1]))
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        for resp in responses:
            for dict in resp['results']:
                if dict['solved']:
                    ids.append(dict['puzzle_id'])
        
    return ids



async def asyncGST(key):
    ids = await getIds(key)
    times = []


    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = [asyncGMS(session, key, puzzle_id) for puzzle_id in ids]
        times = await asyncio.gather(*tasks)

    return times

def getSolveTimes(user=None, password=None, key=None):
    if not key:
        key = login(user, password)
    times = asyncio.run(asyncGST(key))
    return times
                                                                        


