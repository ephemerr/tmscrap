# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 00:51:37 2021

@author: admin
"""

import scrap_tools as tools

import re
import warnings
import json


def parse_managers_available(page_num=1):
    pageSoup = tools.get_soup("/manager/verfuegbaremanager/statistik?page=" + str(page_num))
    items = pageSoup.find("table", {"class": "items"})
    rows = items.tbody.contents
    rows = [x for x in rows if x != '\n']

    def row_parser(row):
        res = {}
        try:
            td_list = row.find_all("td")
            res['name']=td_list[2].a['title']
            res['link']=td_list[2].a['href']
            res['age']=''.join(filter(str.isdigit, td_list[3].text))
            res['since'] = td_list[4].text
            res['last_club_name'] = td_list[7].a.text
            res['last_club_link'] = td_list[7].a['href']
        except Exception:
            warnings.warn(f"Can't parse manager's record: {row}")
            return {}
        return res

    res = list(filter(None, map(row_parser, rows)))
    return res

def parse_career(url):
    pageSoup = tools.get_soup(url)
    items = pageSoup.find("table",{"class": "items"})
    rows = items.tbody.contents
    rows = [x for x in rows if x != '\n' and "Sporting Director" in str(x)]

    def row_parser(row):
        td_list = row.find_all("td")
        res = {}
        try:
            res['club_link']=td_list[0].a['href']
            res['club_name']=td_list[0].img['alt']
            res['appointed_season'], res['appointed_date'] = date_fix(td_list[2].text)
            res['until_season'],res['until_date'] = date_fix(td_list[3].text)
        except Exception:
            warnings.warn(f"Can't parse manager's career: {td_list}")
            return {}
        return res

    res = list(filter(None,map(row_parser, rows)))
    return res


def parse_all_club_transfers(club):
    pageSoup = tools.get_soup(club)
    headers = pageSoup.find_all("div",{"class": "table-header"})
    tables = [t.parent for t in headers if "Arrivals" in str(t) ]

    def table_parser(table):
        records = []
        tbody = table.find("tbody")
        if tbody: records = tbody.find_all("tr",{"class":""})

        def row_parser(record):
            tds = record.find_all("td")
            transfer={}
            try:
                transfer['player_name'] = tds[0].a['title']
                transfer['player_link'] = tds[0].a['href']
                transfer['from_name'] = tds[1].a.img['alt']
                transfer['from_link'] = tds[1].a['href']
                transfer['fee'] = tds[3].text
            except Exception:
                warnings.warn(f"Can't parse club transfers: {tds}")
                return {}
            return transfer

        return list(filter(None,map(row_parser, records)))

    return list(map(table_parser, tables))

def parse_club_transfers_by_season(club):
    pageSoup = tools.get_soup(club)
    headers = pageSoup.find_all("div",{"class": "table-header"})
    tables = [t.parent for t in headers if "Arrivals" in str(t) ]

    def table_parser(table):
        records_ = []
        tbody = table.find("tbody")
        if tbody: records_ = list(tbody.children)[1:][::2]
        records = [r for r in records_ if not "End of loan" in str(r)]

        def row_parser(record):
            tds = record.find_all("td")
            if len(tds) < 12: return {}
            transfer={}
            try:
                transfer['player_name'] = tds[1].a['title']
                transfer['player_link'] = tds[1].a['href']
                transfer['age'] = int(tds[5].text)
                transfer['from_name'] = tds[8].a.img['alt']
                transfer['from_link'] = tds[8].a['href']
                if tds[10].a:
                    transfer['league_country'] = tds[10].img['title']
                    transfer['league_link'] = tds[10].a['href']
                    transfer['league_name'] = tds[10].a['title']
                transfer['fee'] = tds[11].a.text
                transfer['transfer_link'] = tds[11].a['href']
                transfer['to_link'] = club
            except Exception:
                warnings.warn(f"Can't parse club's transfer: {tds}")
                return {}
            return transfer

        return list(filter(None, map(row_parser, records)))

    return [tr for tr in table_parser(tables[0]) if not 'loan' in tr['fee'].lower()]

def parse_players_transfers(player):
    pageSoup = tools.get_soup(player)
    desc = pageSoup.find("meta", {"name":"description"})
    match = re.match(".+Market value: ([^ ]+) .+", str(desc))
    value = ""
    if match: value = match.group(1)
    table = pageSoup.find("div",{"class": "responsive-table"}).tbody
    rows = table.find_all("tr",{"class":"zeile-transfer"})
    def parse_row(row):
        tds = row.find_all("td")
        transfer={}
        try:
            if not tds[7].a or "Retired" in str(tds): return {}
            transfer['season'] = tds[0].text
            transfer['date'] = tds[1].text
            transfer['from_name']=tds[2].a.img['alt']
            transfer['from_link']=tds[2].a['href']
            transfer['to_name'] = tds[7].a.text
            transfer['to_link'] = tds[7].a['href']
            transfer['value'] = tds[8].text
            transfer['fee'] = tds[9].text
            transfer['transfer_link']=tds[10].a['href']
        except Exception:
            warnings.warn(f"Can't parse player's transfer: {tds}")
            return {}
        return transfer
    return list(filter(None,map(parse_row, rows))), value

def transfer_update_from_profile(transfer):
    player_transfers,value = parse_players_transfers(transfer['transfer_link'])
    for t in player_transfers:
        if 'to_link' in t and t['from_link'] == transfer['from_link'] and t['to_link'] == transfer['to_link'] and not "loan" in t['fee'].lower():
            transfer['date'] = t['date']
            transfer['value'] = t['value']
            break
    if not 'date' in transfer:
        warnings.warn(f"Can't update transfer date: {transfer}")
    for t in reversed(player_transfers):
        if datetime_from_tm(t['date']) > datetime_from_tm(transfer['date']) and not 'loan' in t['fee'].lower():
            transfer['sold'] = t['fee']
            break
    if not 'sold' in transfer:
        transfer['sold'] = value
    return transfer

def sportdir_seasons(manager_url):
    res = []
    def seasons_range(since,until):
        return range(dict_seasons[since], dict_seasons[until]+1)

    career = parse_career(manager_url)
    for step in career:
        seasons = seasons_range(step["appointed_season"], step['until_season'])
        club = step["club_link"].replace("startseite","transfers")
        for year in seasons:
            club = club[:-4] + str(year)
            season = {}
            season['link'] = club
            if year == seasons[0]:
                season['appointed_date'] = step['appointed_date']
            if year == seasons[-1]:
                season['until_date'] = step['until_date']
            res.append(season)
    return res

def sportdir_buys(manager_url) :
    seasons = sportdir_seasons(manager_url)
    arrivals = []
    for season in seasons:
        sleep_pause()
        season_arrivals = parse_club_transfers_by_season(season['link'])
        for a in season_arrivals:
            sleep_pause()
            a = transfer_update_from_profile(a)
        if 'appointed_date' in season:
            season_arrivals = [a for a in season_arrivals if datetime_from_tm(a['date']) > datetime_from_tm(season['appointed_date'])]
        if 'until_date' in season:
            season_arrivals = [a for a in season_arrivals if datetime_from_tm(a['date']) < datetime_from_tm(season['until_date'])]
        arrivals.extend(season_arrivals)
    return arrivals

def collect_managers_page(page):
    dataset = []
    try:
        managers = parse_managers_available(page)
    except Exception:
        warnings.warn(f"Can't parse managers page: {i}")
        return []
    for man in managers:
        try:
            buys = sportdir_buys(man['link'])
        except Exception:
            warnings.warn(f"Can't parse manager's profile: {man['name']}")
            continue
        dataset.append([man, buys])
    return dataset

def collect_managers_data():
    dataset = []
    for i in range(1,5):
        sleep_pause()
        try:
            managers = parse_managers_available(i)
        except Exception:
            warnings.warn(f"Can't parse managers page: {i}")
            continue
        for man in managers:
            try:
                buys = sportdir_buys(man['link'])
            except Exception:
                warnings.warn(f"Can't parse manager's profile: {man['name']}")
                continue
            dataset.append([man, buys])
    with open("dataset.json", "w") as fp:
        json.dump(dataset , fp)
    print(len(dataset))
    return dataset
