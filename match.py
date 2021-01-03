from team import Team


class Match:
    match_id_counter = 0

    def __init__(self, team1=Team(), team2=Team(), victor=Team(), season_title="", event=""):
        self.match_id = Match.match_id_counter
        self.team1 = team1
        self.team2 = team2
        self.victor = victor
        self.season_title = season_title
        self.event = event

        Match.match_id_counter += 1

    def to_database(self, db):
        cursor = db.cursor()

        sql_insert_items = [F"INSERT INTO `match` VALUES({self.match_id}",
                            F"\"{self.team1.name}\"",
                            F"\"{self.team2.name}\"",
                            F"\"{self.victor.name}\"",
                            F"\"{self.season_title}\"",
                            F"\"{self.event}\""]
        sql_insert = ",".join(sql_insert_items)
        sql_insert = "".join([sql_insert, ");"])

        cursor.execute(sql_insert)
        db.commit()
