from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from bs4 import BeautifulSoup
import time
import random

import tmsearch
import parsers
from tmsearch import TmSearchDriver

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'")
driver = webdriver.Chrome(options=chrome_options)
num_of_tries = 3

def parse_match(address):
    res = []
    try:
        driver.get(address)
        time.sleep(random.uniform(.5,1))
        len(driver.page_source)
    except:
        print(f"Failed to load page: {address}")
        return res
    try:
        soup = BeautifulSoup(driver.page_source)
        trs = soup.select_one("#live-player-stats").find_all("tr")
    except:
        print(f"Failed to find player stats: {address}")
        return res
    if len(trs) < 30:
        print(f'Number of player stats: {len(trs)}')
        return res
    for tr in trs[1:]:
        try:
            record = {}
            tds = tr.find_all("td")
            if not tds:
                continue
            record["name"] = tds[0].a.span.text
            record["age"] = int(tds[0].select_one("span.player-meta-data").text)
            record["rating"] = tr.select_one("td.rating").text
            record["position"] = tds[0].select("span")[4].text[1:].strip()
        except:
            print(f"Failed to parse: {tr}")
        res.append(record)
    return sorted(res, key=lambda d: d['rating'], reverse=True)

address = "https://ru.whoscored.com/Regions/182/Tournaments/77/Seasons/9153/Stages/21079/Fixtures/%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F-1-2022-2023"

def parse_month(address):
    stats = []
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(address)
    soup = BeautifulSoup(driver.page_source)
    rows = soup.select("a.match-link")
    for row in reversed(rows):
        link = "https://whoscored.com" + row['href'].replace("MatchReport", "LiveStatistics")
        if "Preview" in link:
            continue
        for i in range(0, num_of_tries):
            match_stats = parse_match(link)
            if len(match_stats):
                break
        print(link, len(match_stats))
        match_names = set( player['name'] for player in match_stats )
        saved_names = set( player['name'] for player in stats )
        if set(saved_names).isdisjoint(match_names):
            match_stats[0]['best'] = True
            for player in match_stats[1:]:
                player['best'] = False
            stats.extend(match_stats)
        else:
            break
    return stats

week_stats = sorted(parse_month(address), key=lambda d: d['rating'], reverse=True)

filed_week_stats = [d for d in week_stats if d.get('age') <= 23 and d.get('position') != "GK"]
gk_week_stats = [d for d in week_stats if d.get('age') <= 25 and d.get('position') == "GK"]
gk_week_stats[0]

filed_week_stats[0:10]

# def tm_enrich(players_list):
prefix="https://www.transfermarkt.com"
tm_searcher  = TmSearchDriver()
for player in filed_week_stats[0:10]:
    print(player["name"])
    try:
        profile_link = tm_searcher.search(player["name"].split()[-1], player["age"])
        profile_stats = parsers.player_profile_parser(profile_link.removeprefix(prefix))
        player["photo"] = profile_stats["photo"].replace("big","home3")
        player["tm_position"] = profile_stats["position"].split()[0]
    except Exception as e:
        print(e.message, e.__traceback__, e.__cause__, e.__context__, e.__notes__)

