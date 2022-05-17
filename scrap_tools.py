# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 00:51:37 2021

@author: admin
"""

import requests
from bs4 import BeautifulSoup
#import pandas as pd
import time
import random
import datetime

## Season
dict_seasons = { '80/81' : 1980,
                 '81/82' : 1981,
                 '82/83' : 1982,
                 '83/84' : 1983,
                 '84/85' : 1984,
                 '85/86' : 1985,
                 '86/87' : 1986,
                 '87/88' : 1987,
                 '88/89' : 1988,
                 '89/90' : 1989,
                 '90/91' : 1990,
                 '91/92' : 1991,
                 '92/93' : 1992,
                 '93/94' : 1993,
                 '94/95' : 1994,
                 '95/96' : 1995,
                 '96/97' : 1996,
                 '97/98' : 1997,
                 '98/99' : 1998,
                 '99/00' : 1999,
                 '00/01' : 2000,
                 '01/02' : 2001,
                 '02/03' : 2002,
                 '03/04' : 2003,
                 '04/05' : 2004,
                 '05/06' : 2005,
                 '06/07' : 2006,
                 '07/08' : 2007,
                 '08/09' : 2008,
                 '09/10' : 2009,
                 '10/11' : 2010,
                 '11/12' : 2011,
                 '12/13' : 2012,
                 '13/14' : 2013,
                 '14/15' : 2014,
                 '15/16' : 2015,
                 '16/17' : 2016,
                 '17/18' : 2017,
                 '18/19' : 2018,
                 '19/20' : 2019,
                 '20/21' : 2020,
                 '21/22' : 2021,
                 '22/23' : 2022,
                 '23/24' : 2023
               }

def sleep_pause():
    time.sleep(random.uniform(.3,1))

def get_soup(url_):
    """Makes an http request and returns the html as BeautifulSoup."""

    headers = {'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    )}

    url = "https://www.transfermarkt.com" + url_
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        print("Failed with input url: " + url)

    return BeautifulSoup(response.content, 'html5lib')

def datetime_from_tm(date):
    if not date: return datetime.datetime()
    return datetime.datetime.strptime(date, "%b %d, %Y").date()

def date_fix(date_raw):
    date_raw = date_raw.strip()
    if "expected" in date_raw:
        return "22/23", "Jun 30, 2022" #FIXME
    if date_raw in dict_seasons:
        return date_raw,"Jan 1, " + str(dict_seasons[date_raw])
    match = re.search('(.*) \((.*)\)', date_raw)
    if match:
        return match.group(1),match.group(2)
    else:
        warnings.warn(f"Can't parse date: '{date_raw}'")
        return ""

