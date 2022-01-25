# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 22:32:39 2021

@author: admin
"""

import scrap_tools as tools

import warnings
import json

team="/russia/kader/verein/3448"
year = 2021
def parse_national_team(team="/russia/kader/verein/3448", year=2021):
    pageSoup = tools.get_soup(f"{team}/saison_id/{year}/plus/1")
    items = pageSoup.find("table", {"class": "items"})
    rows = [x for x in items.tbody.contents if x != '\n']
    row = rows[0]
    def row_parser(row):
        res = {}
        try:
            tds = row.find_all("td")
            res['position'] = tds[0]['title']
            res['name'] = tds[3].span.a['title']
            res['link'] = tds[3].span.a['href']
            res['birthdate'] = tds[5].text
            res['club'] = tds[6].img['alt']
            res['club_link'] = tds[6].a['href'] 
            res['heigh'] = tds[7].text
            res['foot'] = tds[8].text            
            res['matches'] = tds[9].text
            res['goals'] = tds[10].text
            res['debut'] = tds[11].text
            res['market_value'] = tds[12].text
        except Exception:
            warnings.warn(f"Can't parse team record: {row}")
            return {}
        return res
    row_parser.counter = 1
    res = list(filter(None, map(row_parser, rows)))    
    return res

def collect_national_team_peformance(team, num_of_years=1):
    res = []
    for year in range(2022 - num_of_years, 2022):
        print(year)
        tools.sleep_pause()
        try:
            stats = parse_national_team(team, year)
            for record in stats:
                record['year'] = year
            res.extend(stats)
        except Exception:
            warnings.warn(f"Can't parse year: {year}")
            continue
    with open("json\\nt_performance.json", "w") as fp:
        json.dump(res , fp)
        
    return res        

collect_national_team_peformance("/russia/kader/verein/3448", 29)