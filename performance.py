# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 03:17:42 2021

@author: admin
"""

import scrap_tools as tools

import warnings
import json
import functools

def page_parser(func):
    @functools.wraps(func)
    def inner(address):
        pageSoup = tools.get_soup(address)
        items = pageSoup.find("table", {"class": "items"})
        rows = items.tbody.contents
        rows = [x for x in rows if x != '\n']
        row = rows[0]
        res = []
        setattr(inner, "counter",  1)
        for row in rows:
            try:
                parsed = func(row)
                if parsed:
                    res.append(parsed)
            except Exception:
                warnings.warn(f"Can't parse {address}:\n{row}\nby: {func.__name__}")
        return res
    return inner


@page_parser
def league_parser(row):
    res = {}
    tds = row.find_all("td")
    if len(tds) < 8: return 
    res['name']=tds[0].img['alt']
    res['link']=tds[0].a['href']
    res['size']=tds[3].a.text
    res['average_age'] = tds[4].text
    res['foreigners'] = tds[5].text
    res['average_market_value'] = tds[6].text
    res['total_market_value'] = tds[7].text
    res['pos'] = league_parser.counter
    league_parser.counter += 1
    return res

@page_parser
def team_performance_parser(row):
    res = {}
    tds = row.find_all("td")
    res['position']=tds[0]['title']
    res['number']=tds[0].div.text
    tds[3]
    res['name'] = tds[3].span.a['title']
    res['link'] = tds[3].span.a['href']
    res['age'] = tds[5].text
    res['country'] = [ flag['title'] for flag in tds[6].contents if "title" in flag.attrs ]
    res['in squad'] = tds[7].text
    res['appearances'] = tds[8].text
    res['goals'] = tds[9].text
    res['assists'] = tds[10].text
    res['yellows'] = tds[11].text
    res['yellow/reds'] = tds[12].text
    res['reds'] = tds[13].text
    res['sub_on'] = tds[14].text
    res['sub_off'] = tds[15].text
    res['ppg'] = tds[16].text
    res['time'] = tds[17].text
    return res

@page_parser
def team_startseite_parser(row):
    res = {}
    tds = row.find_all("td")
    res['position']=tds[0]['title']
    res['number']=tds[0].div.text
    res['name'] = tds[3].span.a['title']
    res['link'] = tds[3].span.a['href']
    res['age'] = tds[6].text
    res['country'] = [ flag['title'] for flag in tds[7].contents if "title" in flag.attrs ]
    return res
    
address = "/wettbewerbe/europa"

@page_parser
def continent_parser(row):
    res = {}
    tds = row.find_all("td")
    if len(tds) < 9: return 
    res['name'] = tds[2].a.text
    res['link'] = tds[2].a['href']
    res['country'] = tds[3].img['title']
    res['clubs'] = tds[4].text
    res['players'] = tds[5].text
    res['average_age'] = tds[6].text
    res['foreigners'] = tds[7].text
    res['total_value'] = tds[9].text
    res['pos'] = continent_parser.counter
    continent_parser.counter += 1
    return res


address = "/sardar-azmoun/leistungsdatendetails/spieler/180337"
@page_parser
def career_detailed_stats_parser(row):
    res = {}
    tds = row.find_all("td")
    res['season'] = tds[0].text
    res['competition_name'] = tds[2].a['title']
    res['competition_link'] = tds[2].a['href']
    res['club_name'] = tds[3].a['title']
    res['club_link'] = tds[3].a['href']
    res['appearances'] = tds[4].a.text
    res['goals'] = tds[5].text
    res['assists'] = tds[6].text
    res['time'] = tds[8].text
    return res

def collect_ex_pfl_players(league, num_of_years=1):
    res = []
    league_short = league.split('/')[-1]
    for year in range(2022 - num_of_years, 2022):
        print(league_short, year)
        tools.sleep_pause()
        try:
            adress = f"{league}/plus/?saison_id={year}"
            teams = league_parser(adress) 
            for team in teams:
                print(team["name"])
                tools.sleep_pause()
                try:
                    performance_link = team['link']
                    print(performance_link)
                    stats = team_startseite_parser(performance_link)
                    for record in stats:
                        print(team['name'], record['name'])
                        record['team'] = team
                        record['year'] = year
                        record['league'] = league_short
                        tools.sleep_pause()
                        career_link = record['link'].replace("profil", "leistungsdatendetails")
                        seasons = career_detailed_stats_parser(career_link)
                        for season in seasons:
                            if "PFL" in season['competition_name'] or "FNL-2" in season['competition_name']:
                                res.append({"player": record['name'], "pfl_year": season['season']})
                                break
                except Exception:
                    warnings.warn(f"Can't parse team: {team['link']}")
                    continue
        except Exception:
            warnings.warn(f"Can't parse year: {year} for {league_short}")
            continue
    with open("from_pfl.json", "w") as fp:
        json.dump(res , fp)
        print(f"{league_short} parsed")
    return res    

def collect_league_peformance(league, num_of_years=1):
    res = []
    league_short = league.split('/')[-1]
    for year in range(2022 - num_of_years, 2022):
        print(league_short, year)
        tools.sleep_pause()
        try:
            adress = f"{league}/plus/?saison_id={year}"
            teams = league_parser(adress) 
            for team in teams:
                tools.sleep_pause()
                try:
                    performance_link = team['link'].replace("startseite", "leistungsdaten").replace("saison_id/", "reldata/%26") + "/plus/1"
                    stats = team_performance_parser(performance_link)
                    for record in stats:
                        record['team'] = team
                        record['year'] = year
                        record['league'] = league_short
                    res.extend(stats)
                except Exception:
                    warnings.warn(f"Can't parse team: {team['link']}")
                    continue
        except Exception:
            warnings.warn(f"Can't parse year: {year} for {league_short}")
            continue
    with open(f"json\\performance_{league_short}.json", "w") as fp:
        json.dump(res , fp)
        print(f"{league_short} parsed")
    return res

def collect_continent(address):
    res = []
    leagues = continent_parser(address)
    with open(f"europe_leagues.json", "w") as fp:
        json.dump(leagues , fp)
    with open(f"europe_leagues.json") as data_file:
        data = json.load(data_file)
    df = pd.json_normalize(data)
    df.reset_index().to_csv("europe_leagues.csv")
        
    # for league in leagues:
    #     league_performance = collect_league_peformance(league['link'], 30)
    #     res.extend(league_performance)
    #     with open("json\\performance_top20.json", "w") as fp:
    #         json.dump(res , fp)


