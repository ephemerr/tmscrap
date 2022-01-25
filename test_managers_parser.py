# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 01:26:58 2021

@author: admin
"""

import managers_parser as mp
import scrap_tools as tools

import random as rand
import unittest
import json

def get_random_manager():
    page = rand.randint(1,30)
    res = mp.parse_managers_available(page)
    return rand.choice(res)


def get_random_club():
    career = []
    while not career:
        tools.sleep_pause()
        man = get_random_manager()['link']
        career = mp.parse_career(man)
    return rand.choice(career)['club_link']


def get_random_player():
    transfers = []
    club = get_random_club()
    while not transfers:
        tools.sleep_pause()
        transfers = mp.parse_club_transfers_by_season(club.replace("startseite","transfers"))
    return rand.choice(transfers)['player_link']

class TestFactorial(unittest.TestCase):

    def test_parse_managers_available(self):
        tools.sleep_pause()
        manager_keys = ['name', 'link', 'age', 'since', 'last_club_name', 'last_club_link']
        page = rand.randint(1,30)
        res = mp.parse_managers_available(page)
        self.assertEqual(len(res), 25)
        for r in res:
            for k in manager_keys:
                self.assertIn(k, r)

    def test_parse_career(self):
        tools.sleep_pause()
        managers = [get_random_manager()['link'],"/massimiliano-mirabelli/profil/trainer/50151" ]
        keys = ['club_link', 'club_name','appointed_season','appointed_date', 'until_season', 'until_date']
        for manager in managers:
            res = mp.parse_career(manager)
            for r in res:
                for k in keys:
                    self.assertIn(k, r)

    def test_parse_club_transfers_by_season(self):
        tools.sleep_pause()
        clubs = [get_random_club(), "/stk-1914-samorin/transfers/verein/34775/saison_id/2017"]
        for club in clubs:
            res = mp.parse_club_transfers_by_season(club.replace("startseite","transfers"))
            keys = ['player_name', 'player_link', 'age', 'from_link', 'from_name', 'fee', 'transfer_link', 'to_link']
            for r in res:
                for k in keys:
                    self.assertIn(k, r)
        return res

    def test_parse_players_transfers(self):
        players = [get_random_player(), "/raffaele-biancolino/transfers/spieler/25486/transfer_id/3087692"]
        for player in players:
            res,value = mp.parse_players_transfers(player)
            keys = ['season', 'date', 'value', 'from_link', 'from_name', 'fee', 'transfer_link', 'to_link']
            for r in res:
                for k in keys:
                    self.assertIn(k, r)

    def test_sportdir_buys(self):
          man = get_random_manager()
          buys = mp.sportdir_buys(man['link'])
          with open(f"json\\{man['name']} buys.json", "w") as fp:
              json.dump(buys , fp)

    # def test_collect_data(self):
    #     mp.collect_managers_data()

if __name__ == '__main__':
    unittest.main()

