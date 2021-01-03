import re


class Team:
    def __init__(self, name="", active_season_title="", players=[]):
        self.name = name
        self.active_season_title = active_season_title
        self.players = players

    def has_player(self, player_name):
        return player_name in self.players

    def has_player(self, player):
        return player.name in self.get_player_names()

    def add_player(self, player):
        self.players.append(player)

    def to_database(self, db):
        cursor = db.cursor()

        sql_insert_items = [F"INSERT INTO team VALUES(\"{self.name}\"",
                            F"\"{self.active_season_title}\"",
                            F"\"{self.players[0].name}\"",
                            F"\"{self.players[1].name}\"",
                            F"\"{self.players[2].name}\""]
        sql_insert = ",".join(sql_insert_items)
        sql_insert = "".join([sql_insert, ");"])

        cursor.execute(sql_insert)
        db.commit()

    def __str__(self):
        team_string = [self.name,
                       "*******",
                       self.players[0].name,
                       self.players[1].name,
                       self.players[2].name,
                       "*******"]
        team_string = "\n".join(team_string)
        return team_string
