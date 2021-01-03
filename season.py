class Season:
    # def build_multiseason_pf_matrix(seasons, season_filter=None, player_filter=None):

    def __init__(self, title, player_dict, team_set, matches):
        self.title = title
        self.player_dict = player_dict
        self.team_set = team_set
        self.matches = matches

    def to_database(self, db):
        for team in self.team_set:
            team.to_database(db)
        for match in self.matches:
            match.to_database(db)

    # def from_database(self, db):

    # def build_performance_matrix(self):
