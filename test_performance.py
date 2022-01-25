# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 10:11:31 2021

@author: admin
"""

import scrap_tools as tools
import performance as pe

import random as rand
import unittest
import json

class TestPerformance(unittest.TestCase):
    # def test_parse_league(self):
         league = "/protathlima-cyta/startseite/wettbewerb/ZYP1"
    #     year = 2020
    #     res1 = pe.parse_league_season_teams(league,year)
    #     res2 = pe.league_parser(league, year)
    #     self.assertEqual([], [i for i in res1 if i not in res2]);

    def test_parse_team(self):
        address = "/zob-ahan-isfahan/startseite/verein/6081/saison_id/2019"
        res1 = pe.parse_team_stats(address)
        performance_link = address.replace("startseite", "leistungsdaten").replace("saison_id/", "reldata/%26") + "/plus/1"
        res2 = pe.team_parser(performance_link)
        self.assertEqual([], [i for i in res1 if i not in res2]);

if __name__ == '__main__':
    unittest.main()


