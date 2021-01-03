import re

import numpy as np
import pandas as pd
from sklearn import preprocessing


class Player:
    player_count = 0

    def __init__(self, name, player_id, games_played=None, win_perc=None, scpg=None, gpg=None, apg=None, sapg=None, shpg=None,
                 tot_score=None, tot_goals=None, tot_assists=None, tot_saves=None, tot_shots=None, tot_ht=None,
                 tot_savior=None, tot_pm=None, tot_mvp=None, sc_perc_of_team=None, g_perc_of_team=None,
                 a_perc_of_team=None, sa_perc_of_team=None, sh_perc_of_team=None, avg_scb_pos=None,
                 assist_goal_ratio=None, sh_perc=None, goal_part=None):
        self.name = name
        self.player_id = player_id
        self.games_played = games_played
        self.win_perc = win_perc
        self.scpg = scpg
        self.gpg = gpg
        self.apg = apg
        self.sapg = sapg
        self.shpg = shpg
        self.tot_score = tot_score
        self.tot_goals = tot_goals
        self.tot_assists = tot_assists
        self.tot_saves = tot_saves
        self.tot_shots = tot_shots
        self.tot_ht = tot_ht
        self.tot_savior = tot_savior
        self.tot_pm = tot_pm
        self.tot_mvp = tot_mvp
        self.sc_perc_of_team = sc_perc_of_team
        self.g_perc_of_team = g_perc_of_team
        self.a_perc_of_team = a_perc_of_team
        self.sa_perc_of_team = sa_perc_of_team
        self.sh_perc_of_team = sh_perc_of_team
        self.avg_scb_pos = avg_scb_pos
        self.assist_goal_ratio = assist_goal_ratio
        self.sh_perc = sh_perc
        self.goal_part = goal_part

        Player.player_count += 1

    def format_perc_attr(self, attr_name):
        attr = getattr(self, attr_name)
        attr = attr.replace('.', '')
        attr = attr.replace('%', '')
        attr = "".join(['.', attr])

        setattr(self, attr_name, attr)

    def to_database(self, db):
        player_attr_names = self.__dir__()
        cursor = db.cursor()

        # Lazy reflection... no other reason to use this other than it reducing the amount of code on this page.
        # Will it slow down performance significantly? Probably not...
        player_attr_names = self.__dir__()
        index_for_slice = player_attr_names.index("__module__")
        player_attr_names = player_attr_names[:index_for_slice]

        sql_insert_items = [F"INSERT INTO player VALUES(\"{str(getattr(self, player_attr_names[0]))}\""]
        for player_attr in player_attr_names[1:]:
            if re.search("perc|part", player_attr):
                self.format_perc_attr(player_attr)
            sql_insert_items.append(F"{str(getattr(self, player_attr))}")
        sql_insert = ",".join(sql_insert_items)
        sql_insert = "".join([sql_insert, ");"])

        cursor.execute(sql_insert)
        db.commit()

    def __str__(self):
        player_stat_string = ["---------------------------------------",
                              "PLayer name: " + self.name,
                              "Games played: " + str(self.games_played),
                              "Win percentage: " + str(self.win_perc),
                              "Shooting percentage: " + str(self.sh_perc),
                              "Average score per game: " + str(self.scpg),
                              "Average goals per game: " + str(self.gpg),
                              "Average assists per game: " + str(self.apg),
                              "Average saves per game: " + str(self.sapg),
                              "Average shots per game: " + str(self.shpg),
                              "Total score: " + str(self.tot_score),
                              "Total goals: " + str(self.tot_goals),
                              "Total assists: " + str(self.tot_assists),
                              "Total saves: " + str(self.tot_saves),
                              "Total shots: " + str(self.tot_shots),
                              "Total hat tricks: " + str(self.tot_ht),
                              "Total saviors: " + str(self.tot_savior),
                              "Total playmakers: " + str(self.tot_pm),
                              "Total mvp's: " + str(self.tot_mvp),
                              "Average percentage of team score: " + str(self.sc_perc_of_team),
                              "Average percentage of team goals: " + str(self.g_perc_of_team),
                              "Average percentage of team assists: " + str(self.a_perc_of_team),
                              "Average percentage of team saves: " + str(self.sa_perc_of_team),
                              "Average percentage of team shots: " + str(self.sh_perc_of_team),
                              "Average scoreboard position: " + str(self.avg_scb_pos),
                              "Assist to goal ratio: " + str(self.assist_goal_ratio),
                              "Goal participation: " + str(self.goal_part),
                              "---------------------------------------"]
        return "\n".join(player_stat_string)

    def __del__(self):
        Player.player_count -= 1
