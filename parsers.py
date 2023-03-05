import scrap_tools as tools
import warnings
import functools
import re

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
    if len(tds) < 7: raise Exception("Number of values isn't enough")
    res['name']=tds[0].img['alt']
    res['link']=tds[0].a['href']
    res['size']=tds[2].a.text
    res['average_age'] = tds[3].text
    res['foreigners'] = tds[4].text
    res['average_market_value'] = tds[5].text
    res['total_market_value'] = tds[6].text
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

@page_parser
def team_kader_parser(row):
    res = {}
    tds = row.find_all("td")
    res['number'] = tds[0].text
    res['position'] = tds[1].tbody.contents[2].td.text.strip()
    res['name'] = tds[3].a.text.strip()
    res['link'] = tds[3].a['href']
    res['age'] = tds[5].text[-3:-1]
    res['country'] = tds[6].contents[0]["title"] 
    res['height'] = tds[7].text
    res['foot'] = tds[8].text
    res['joined'] = tds[9].text[-4:]
    res['contract'] = tds[11].text[-4:]
    res['martket_value'] = tds[12].text
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

def transfers_parser(row):
    res = {}
    cells = row.find_all("div")
    res['year'] = cells[0].text
    res['date'] = cells[1].text
    res['from_club_name'] = cells[2].text
    res['from_club_link'] = cells[2].a['href']
    res['to_club_name'] = cells[3].text
    res['to_club_link'] = cells[3].a['href']
    res['market_value'] = cells[4].text
    res['fee'] = cells[5].text
    return {k: v.strip() for k, v in res.items()}


def player_profile_parser(player):
    player = "/tomas-vaclik/profil/spieler/64000"
    player = "/yusuf-yazici/profil/spieler/386726"
    player = "/artem-ntumba-muamba/profil/spieler/558688"
    pageSoup = tools.get_soup(player)    
    items = pageSoup.find("div", {"class": "large-6 large-pull-6 small-12 columns spielerdatenundfakten"})
    tds = items.div.find_all("span")
    res = {}
    res['age'] = tds[8].text
    res['height'] = tds[10].text
    res['citizenship'] = tds[12].img["title"]
    res['position'] = tds[14].text
    res['foot'] = tds[16].text

    desc = pageSoup.find("meta", {"name":"description"})
    match = re.match(".+Market value: ([^ ]+) .+", str(desc))
    value = ""
    if match: value = match.group(1)
    res["value"] = value
    
    table = pageSoup.find("div",{"data-viewport": "Transferhistorie"})
    rows = table.find_all("div",{"class":"grid tm-player-transfer-history-grid"})
    row = rows[0]    
    res["transfers"] = list(filter(None,map(transfers_parser, rows)))
    return res


