from player import Player
import numpy as np
from subprocess import Popen

import MySQLdb


def dir_player_test():
    player = Player("Random", 0)
    print(player.__dir__())


def my_sql_query():
    try:
        db = MySQLdb.connect("localhost", "root", "toodles!?13", "player_game")
    except Exception as e:
        Popen(args="D:\\Programming Projects\\PersonalProjects\\RLCSChampionClassifier\\StartMySQL-C.bat")


def main():
    dir_player_test()
    # my_sql_query()


main()
