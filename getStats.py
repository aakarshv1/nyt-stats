import requests
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as soup 
import csv

#https://github.com/mattdodge/nyt-crossword-stats/blob/master/fetch_puzzle_stats.py
#https://github.com/kyledeanreinford/NYT_Mini_Leaderboard_Scraper


api_key = "1w7x7yDN.jAtJJ6VVZ7ntsAZhjkPT1tqIWft4.2Xhgu3oQluFHQCpzkUGMBi300Qz4jOoea6bgYnRxckKfk3fLpyt0Mds/F//8GbFBc8GNpD9Lb7QDEPbFqPxDTQO38FS1^^^^CBQSLwji2feiBhDo2fOkBhoSMS00ZOHO99EXI8EtNC25BYbRIKjf2iYqAgACOLmC18oFGkBL5M7SQxTLV7qqobyRWxyCm59CFDwjaWu8IUW7vLEjcxP3lDrg1lRDWMMQunm2ztS47dmtewNn1ce390C04VgB"  # Replace with your actual API key
API_ROOT = 'https://nyt-games-prd.appspot.com/svc/crosswords'
PUZZLE_INFO = API_ROOT + '/v2/puzzle/mini-{date}.json'
SOLVE_INFO = API_ROOT + '/v2/game/{game_id}.json'
players = ['Aak', 'Bobo22', 'yjsi', 'Pankek']


# def get_mini_crossword_stats():
#     url = f"https://nyt-games-prd.appspot.com/svc/crosswords/v2/puzzle/mini-2023-06-27.json"
#     response = requests.get(url, 
#         cookies={
#             'NYT-S': api_key,
#         }
#     )
#     print(response)
#     data = json.loads(response.text)
#     puzzle_info = response.json().get('results')[0]

#     solve_resp = requests.get(
#         SOLVE_INFO.format(game_id=puzzle_info['puzzle_id']),
#         cookies={
#             'NYT-S': api_key,
#         },
#     )


#    return json.loads(solve_resp.text)

def getMiniStat(date: str):
    puzzle_resp = requests.get(
        PUZZLE_INFO.format(date=date),
        cookies={
            'NYT-S': api_key,
        },
    )
    puzzle_info = puzzle_resp.json().get('results')[0]
    solve_resp = requests.get(
        SOLVE_INFO.format(game_id=puzzle_info['puzzle_id']),
        cookies={
            'NYT-S': api_key,
        },
    )
    res = json.loads(solve_resp.text)['results']
    print(res)
    if res['solved']:
        return res['timeElapsed']
    return

def getStats(start:str, end=str(datetime.now().isoformat()), incSat=False):
    times = []
    dates = []
    current_date = datetime.fromisoformat(start)
    end_date = datetime.fromisoformat(end)

    while current_date <= end_date:
        date_string = current_date.date().isoformat()
        time = getMiniStat(date_string)
        if time and current_date.weekday()!=5:
            times.append(time)
            dates.append(current_date.day)
        current_date += timedelta(days=1)

    plt.scatter(x=dates, y=times)
    plt.title(f"Mini Crossword Stats for June (no Saturday)")
    plt.xlabel("Date")
    plt.ylabel("Solve Time")
    plt.savefig("results.png")

def get_mini_times(cookie,output):
    url = "https://www.nytimes.com/puzzles/leaderboards"
    response = requests.get(url, cookies={
        'NYT-S': cookie,
    },
    )
    print(response.text)
    page = soup(response.content, features='html.parser')
    solvers = page.find_all('div', class_='lbd-score')
    current_datetime = datetime.fromisoformat("2023-06-27")
    #while current_datetime <= datetime.now():
    month = str(current_datetime.strftime("%m"))
    day = str(current_datetime.strftime("%d"))
    year = str(current_datetime.strftime("%Y"))
    daytimes=[]
    print('--------------------------')
    print("Mini Times for " + month + '-' + day + '-' + year)
    for solver in solvers:
        name = solver.find('p', class_='lbd-score__name').text.strip()
        try:
            time = solver.find('p', class_='lbd-score__time').text.strip()
        except:
            time="--"
        if name.endswith("(you)"):
            name_split = name.split()
            name = name_split[0]
        if name in players:
            daytimes.append([month,day,year,name,time])
    #current_datetime += timedelta(days=1)
    with open(output, 'w') as csvfile:  
        csvwriter = csv.writer(csvfile)              
        csvwriter.writerows(daytimes) 


# Main execution
if __name__ == "__main__":
    #stats = get_mini_crossword_stats()
    #getStats("2023-06-01")
    get_mini_times(api_key, "test.csv")

#https:\u002F\u002Fmyaccount.nytimes.com\u002Fauth\u002Fenter-email?redirect_uri=https%3A%2F%2Fwww.nytimes.com%2Fpuzzles%2Fleaderboards&response_type=cookie&client_id=games&application=crosswords&asset=leaderboard","register":"https:\u002F\u002Fmyaccount.nytimes.com\u002Fauth\u002Fregister?redirect_uri=https%3A%2F%2Fwww.nytimes.com%2Fpuzzles%2Fleaderboards&response_type=cookie&client_id=games&application=crosswords&asset=leaderboard","printDate":"2023-06-29","puzzleLink":"\u002Fcrosswords\u002Fgame\u002Fmini\u002F2023\u002F06\u002F29
