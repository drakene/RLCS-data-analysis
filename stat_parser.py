from abc import ABC
from html.parser import HTMLParser
from player import Player


class StatParserHTML(HTMLParser, ABC):
    # Map of player name to Player object
    player_dict = {}
    # Map of player name to most recently used table to examine that player's stats
    player_table_dict = {}

    # Most recently examined player
    MRE_player = ""
    player_count = 0
    attr_index = 0

    # Upon finishing the parsing of a player's stats on a given table, this list will be used to reset the index of the
    # currently examined stat to match its corresponding element in stat_dict. We don't begin on the index of the exact
    # html element we wish to extract as a stat, as the beginning of each table is populated by games played and
    # win percentage, which I choose to extract from the first table. As such, we need to increment past these stats
    # when parsing the html document and reset attr_index when finished parsing through a player's stats in a table.
    # 0 = Beginning of "Main" (not in list)
    # 8 = Beginning of "Totals"
    # 15 = Beginning of "Percentages"
    # 22 = Beginning of "Medals"
    # 29 = Beginning of "Advanced"
    attr_return_index_list = [8, 15, 22, 29]

    stat_dict = {
        0: "games_played",
        1: "win_perc",
        2: "scpg",
        3: "gpg",
        4: "apg",
        5: "sapg",
        6: "shpg",
        10: "tot_score",
        11: "tot_goals",
        12: "tot_assists",
        13: "tot_saves",
        14: "tot_shots",
        17: "sc_perc_of_team",
        18: "g_perc_of_team",
        19: "a_perc_of_team",
        20: "sa_perc_of_team",
        21: "sh_perc_of_team",
        24: "tot_ht",
        25: "tot_savior",
        26: "tot_pm",
        27: "tot_mvp",
        31: "avg_scb_pos",
        32: "assist_goal_ratio",
        33: "sh_perc",
        34: "goal_part",
    }

    def handle_data(self, data):
        tag = str(self.get_starttag_text())
        has_player_href = tag.find("href=\"/player/")  # Return -1 if the tag does not contain a player's name

        if tag[1:3] == "a " and has_player_href != -1:
            print("Player: " + str(data))
            if data not in StatParserHTML.player_table_dict:  # First time player data is encountered
                StatParserHTML.MRE_player = data
                StatParserHTML.player_dict[data] = Player(data, StatParserHTML.player_count)
                StatParserHTML.player_table_dict[data] = -1  # Set to ind
                StatParserHTML.player_count += 1
                # Reset attr_count to the index of the first table's first exploitable statistic.
                StatParserHTML.attr_index = 0

            else:  # Player already encountered... need to increment tables.
                # Reset attr_count to the index of the currently examined table's first exploitable attribute.
                StatParserHTML.MRE_player = data
                StatParserHTML.player_table_dict[data] += 1
                table_num = StatParserHTML.player_table_dict[data]
                StatParserHTML.attr_index = StatParserHTML.attr_return_index_list[table_num]

        elif tag[1:3] == "td":
            print(data.strip() + ': ' + str(StatParserHTML.attr_index))
            data = data.strip()
            if StatParserHTML.attr_index in StatParserHTML.stat_dict:
                setattr(StatParserHTML.player_dict[StatParserHTML.MRE_player],
                        StatParserHTML.stat_dict[StatParserHTML.attr_index], data)
            StatParserHTML.attr_index += 1
