# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 03:17:42 2021

@author: admin
"""

import parsers
import pandas as pd
import scrap_tools as tools
import warnings
import json


def collect_ex_pfl_players(league, num_of_years=1):
    res = []
    league_short = league.split('/')[-1]
    for year in range(2022 - num_of_years, 2022):
        print(league_short, year)
        tools.sleep_pause()
        try:
            adress = f"{league}/plus/?saison_id={year}"
            teams = parsers.league_parser(adress)
            for team in teams:
                print(team["name"])
                tools.sleep_pause()
                try:
                    performance_link = team['link']
                    print(performance_link)
                    stats = parsers.team_startseite_parser(performance_link)
                    for record in stats:
                        print(team['name'], record['name'])
                        record['team'] = team
                        record['year'] = year
                        record['league'] = league_short
                        tools.sleep_pause()
                        career_link = record['link'].replace("profil", "leistungsdatendetails")
                        seasons = parsers.career_detailed_stats_parser(career_link)
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

def collect_balkans():
    countries =  [  "Greece" , "Serbia" , "Bosnia-Herzegovina" , "Albania" ,
                  "North Macedonia" , "Romania" , "Bulgaria" , "Turkey" ,
                  "Croatia" , "Montenegro" , "Kosovo" , "Slovenia"]
    df = pd.read_csv('europe_leagues.csv')
    res = []
    country = countries[0]
    for country in countries :
        try:
            league = df[df['country'] == country]["link"].values[0]
            league_short = league.split('/')[-1]
            print(country, league_short)
            tools.sleep_pause()
            teams = parsers.league_parser(league)
            team = teams[0]
            for team in teams:
                print(team["name"])
                tools.sleep_pause()
                try:
                    performance_link = team['link'].replace("startseite", "kader") + "/plus/1"
                    print(performance_link)
                    stats = parsers.team_kader_parser(performance_link)
                    for record in stats:
                        print(team['name'], record['name'])
                        record['team'] = team
                        record['league'] = country
                    res.extend(stats)
                except Exception:
                    warnings.warn(f"Can't parse team: {team['link']}")
                    continue
        except Exception:
            warnings.warn(f"Can't parse league: {country}")
            continue
        print(f"{league_short} parsed")
    with open("balkans.json", "w") as fp:
        json.dump(res , fp)
    tools.json_to_csv("balkans")
    print("parsing finished")
            
    return res



def collect_league_peformance(league, num_of_years=1):
    res = []
    league_short = league.split('/')[-1]
    for year in range(2022 - num_of_years, 2022):
        print(league_short, year)
        tools.sleep_pause()
        try:
            adress = f"{league}/plus/?saison_id={year}"
            teams = parsers.league_parser(adress)
            for team in teams:
                tools.sleep_pause()
                try:
                    performance_link = team['link'].replace("startseite", "leistungsdaten").replace("saison_id/", "reldata/%26") + "/plus/1"
                    stats = parsers.team_performance_parser(performance_link)
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

address = "/wettbewerbe/europa?ajax=yw1&page=2"

