# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 01:57:58 2021

@author: admin
"""

import pandas as pd
import json as json
import matplotlib.pyplot as plt
from pandas.plotting import table 
import dataframe_image as dfi
# from pandas_profiling import ProfileReport

short_leagues = {'GB1':"England", 'IT1':'Italia', 'ES1':'Spain', 'L1':'Germany', 'FR1':'France', 'PO1':'Poland', 'RU1':'Russia'}
                 # 'NL1':, 'TR1', 'BE1', 'UKR1', 'GR1', 'A1', 'C1', 'SC1', 'KR1', 'TS1', 'PL1', 'DK1', 'RO1', 'SER1', 'SE1', 'NO1', 'UNG1', 'ZYP1']

def league_performance_preprocess(json_file, feather_file):
    with open(json_file) as data_file:
        data = json.load(data_file)
    for item in data:
        if item['country']: item['country'] = item['country'][0]
        else: item['country'] = "" 
        if isinstance(item['time'],str): item['time'] = int(item['time'].replace("'", "").replace(".","").replace("-","0"))
        if isinstance(item['age'],str): item['age'] = int(item['age'].replace("-","0").replace("†",""))
    df = pd.json_normalize(data)
    df = df[(df['time'] != 0) & (df['age'] != 0) ]
    #df = df[['year','age','country','time', 'name', 'link']]
    for i in df.index:
        first_record = df[df['link'] == df.at[i,'link']].sort_values(by='year', ascending=True)[0:1]
        df.at[i, 'debut'] = int(first_record['year'].values[0])
        df.at[i, 'debut_age'] = int(first_record['age'].values[0])
    df['debut'] = df['debut'].astype(int)
    df['debut_age'] = df['debut_age'].astype(int)        
    df.reset_index().to_feather(feather_file)

json_file = "./json/performance_top20.json"
feather_file = "./feather/performance_europe.feather"
country = "Russia"

league_performance_preprocess(json_file, feather_file)


def plot_performance_by_ages(feather_file, country='Russia'):
    df = pd.read_feather(feather_file)

    total = df.groupby('year')['time'].sum()
    def normalize(serie, total=total):
        res = {}
        for k in total.keys():
            res[k] = serie[k]/total[k] * 100
        return res

    df[(df['country'] == country) & (df['age'] > 23)].groupby('year')['time'].sum()

    a23 = normalize(df[(df['country'] == country) & (df['age'] > 23)].groupby('year')['time'].sum())
    u21 = normalize(df[(df['country'] == country) & (df['age'] <= 21)].groupby('year')['time'].sum())
    u23 = normalize(df[(df['country'] == country) & (df['age'] <= 23)].groupby('year')['time'].sum())
    total = normalize(df[(df['country'] == country)].groupby('year')['time'].sum())

    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    fig.set_size_inches(15, 10)

    ax.plot(list(a23.keys()), list(a23.values()),label=">23")  # Plot some data on the axes
    ax.plot(list(u23.keys()), list(u23.values()),label="u23")  # Plot some data on the axes.
    #ax.plot(list(u21.keys()), list(u21.values()),label="u21")  # Plot some data on the axes.
    ax.plot(list(total.keys()), list(total.values()),label="tatal")  # Plot some data on the axes.
    plt.axvline(x=2005, linestyle='--', label="2005 5+6*")
    plt.axvline(x=2019, linestyle='--', label="2019 8+17")
    plt.xticks(list(u23.keys()), rotation=70)
    ax.legend(bbox_to_anchor=(1, 1), loc='upper left', fontsize=20)
    plt.title(f'% of performance time for players from {country}', fontsize=20)

def plot_leagues_performance_by_ages(df_, leagues):
    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    fig.set_size_inches(15, 10)
    
    for league in leagues:        
        df = df_[df_['league'] == short_leagues[league]]
        country = league
        total = df.groupby('year')['time'].sum()
        def normalize(serie, total=total):
            res = {}
            for k in total.keys():
                res[k] = serie[k]/total[k] * 100
            return res

        df[(df['country'] == country) & (df['age'] > 23)].groupby('year')['time'].sum()

        a23 = normalize(df[(df['country'] == country) & (df['age'] > 23)].groupby('year')['time'].sum())
        u23 = normalize(df[(df['country'] == country) & (df['age'] <= 23)].groupby('year')['time'].sum())
        total = normalize(df[(df['country'] == country)].groupby('year')['time'].sum())

        #ax.plot(list(a23.keys()), list(a23.values()),label=f"{country}>23")  # Plot some data on the axes
        #ax.plot(list(u23.keys()), list(u23.values()),label=f"{country} u23")  # Plot some data on the axes.
        ax.plot(list(total.keys()), list(total.values()),label=f"{country}")  # Plot some data on the axes.
        plt.xticks(list(u23.keys()), rotation=70)
        ax.legend(bbox_to_anchor=(1, 1), loc='upper left', fontsize=20)

# leagues = df0['league'].unique()
# league_dict = {}
# for league in leagues:
#     league_dict[league] = df0[df['league'] == league].country.mode()[0]
# short_leagues = {long:short for short,long in league_dict.items()}

# plot_leagues_performance_by_ages(df, ["Russia","England"])

def plot_debut_ages(feather_file, country='Russia'):
    df = pd.read_feather(feather_file)

    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    df20 = df[(df['country'] == 'Russia') & (df['year'] == 2020) ]
    df20.boxplot(column='debut_age',by='age')
    df20[df20['country'] == 'Russia']['name']
    
    yo = df20[(df20['debut_age'] < 18) ][['name','debut_age','debut']].sort_values(by="debut_age")
    for ind in [15116,15272,14965,15232,15141]:
        yo = yo.drop(ind) 
    yo.to_string()        
    df = df.drop('debute',1)
    df20[df20['time'] > 300].groupby('debut').count().plot()

    df[df['name'] == 'Oleg Aleynik']


def table_to_image(df):
    pd.set_option('max_rows', 5)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.float_format', '{:.2f}'.format)    
    df.table()    
    ax = plt.subplot(111, frame_on=False) # no visible frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    # table(ax, yo[['name','debut']])  # where df is your data frame
    # s = yo.style.hide_index()
    # dfi.export(s,"img.png")

# df0 = df
# leagues = df0['league'].unique()
# league_dict = {}
# for league in leagues:
#     league_dict[league] = df0[df['league'] == league].country.mode()[0]

json_file = "from_pfl_1.json"
feather_file = "from_pfl_1.fea"
def pfl_preprocess(json_file, feather_file):
    with open(json_file) as data_file:
        data = json.load(data_file)
    df = pd.json_normalize(data)
    df.reset_index().to_feather(feather_file)

    df
