from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from bs4 import BeautifulSoup
import time
import random

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'")
driver = webdriver.Chrome(options=chrome_options)
num_of_tries = 3

address = "https://www.whoscored.com/Matches/1647777/LiveStatistics/%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F-%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F-1-2022-2023-%D0%93%D0%B0%D0%B7%D0%BE%D0%B2%D0%B8%D0%BA-%D0%9E%D1%80%D0%B5%D0%BD%D0%B1%D1%83%D1%80%D0%B3%D1%81%D0%BA%D0%B0%D1%8F-%D0%A1%D0%BF%D0%B0%D1%80%D1%82%D0%B0%D0%BA"

def parse_match(address):
    res = []
    try:
        driver.get(address)
        time.sleep(random.uniform(.5,1))
        len(driver.page_source)
    except:
        print(f"Failed to load page: {address}")
        return res
    soup = BeautifulSoup(driver.page_source)
    trs = soup.select_one("#live-player-stats").find_all("tr")
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
filed_week_stats[0:10]
gk_week_stats[0]

