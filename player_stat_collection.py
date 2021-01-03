import time, re
from subprocess import Popen

import MySQLdb

from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from msedge.selenium_tools import Edge, EdgeOptions

from player import Player
from team import Team
from season import Season
from match import Match
from stat_parser import StatParserHTML


class LiquipediaNavListener(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        print(" ".join(["Navigating to:", str(url)]))

    def after_navigate_to(self, url, driver):
        print(" ".join(["Navigated to:", str(url)]))


class TeamDictionaryMaker:
    def __init__(self, team_dict):
        self.team_name_fixes = {
            "NRG eSports": self.nrg_fix,
            "Chiefs eSports Club": self.chiefs_fix,
            "PSG eSports": self.psg_fix,
            "compLexity Gaming": self.complexity_fix,
            "Team Orbit": self.orbit_fix,
            "Supersonic Avengers": self.avengers_fix,
            "Team EnVyUs": self.envy_fix,
            "Susquehanna Soniqs": self.soniqs_fix
        }
        self.team_dict = team_dict

    def nrg_fix(self, team):
        self.team_dict["NRG Esports"] = team
        self.team_dict["NRG eSports"] = team
        team.name = "NRG Esports"

    def chiefs_fix(self, team):
        self.team_dict["Chiefs Esports Club"] = team
        team.name = "Chiefs Esports Club"

    def psg_fix(self, team):
        self.team_dict["PSG Esports"] = team
        team.name = "PSG Esports"

    def complexity_fix(self, team):
        self.team_dict["compLexity Gaming"] = team
        self.team_dict["compLexity"] = team  # Liquipedia uses both for Season 5!

    def orbit_fix(self, team):
        self.team_dict["Orbit eSports"] = team
        team.name = "Orbit eSports"

    def avengers_fix(self, team):
        self.team_dict["S. Avengers"] = team
        self.team_dict[team.name] = team

    def envy_fix(self, team):
        self.team_dict["Team Envy"] = team
        team.name = "Team Envy"

    def soniqs_fix(self, team):
        self.team_dict["Soniqs"] = team
        team.name = "Soniqs"

    def no_fix(self, team):
        self.team_dict[team.name] = team

    def fix_name(self, team):
        method = self.team_name_fixes.get(team.name, self.no_fix)
        method(team)


# We look for:
# * GAMES PLAYED
# * crosstable attributes ---------------> Games played for team
# * <a title="Lachinio" href="/rocketleague/Lachinio">Lachinio</a> ----------> Player on team
# * element" <center> <b> <a title="IBUYPOWER" href="/rocketleague/IBUYPOWER">iBUYPOWER</a> -----------> Team name

# * SEASONS
# * <a title="Rocket League Championship Series/Season 1"
#                           href="/rocketleague/Rocket_League_Championship_Series/Season_1">RLCS Season 1 - Finals</a>


def make_brackets(brackets, bracket_headers, special_case):
    brk_index = 0
    bracket_tuples = []
    if special_case:
        while brk_index < len(brackets):
            if len(brackets[brk_index].find_elements_by_class_name("bracket-game")) == 0:
                brackets.pop(brk_index)
            elif len(brackets[brk_index].find_elements_by_class_name("bracket-header")) == 0:
                bracket_tuples.append((brackets[brk_index], "Semifinals"))
                brk_index += 1
            elif len(bracket_headers[brk_index]) == 0:
                bracket_headers.pop(brk_index)
            elif bracket_headers[brk_index][0].wrapped_element.text == "Qualified":
                bracket_headers.pop(brk_index)
                brackets.pop(brk_index)
            else:
                bracket_tuples.append((brackets[brk_index], bracket_headers[brk_index][0].wrapped_element.text))
                brk_index += 1
    else:
        while brk_index < len(brackets):
            if len(brackets[brk_index].find_elements_by_class_name("bracket-game")) == 0:
                brackets.pop(brk_index)
            elif len(bracket_headers[brk_index]) == 0:
                bracket_headers.pop(brk_index)
            elif bracket_headers[brk_index][0].wrapped_element.text == "Qualified":
                bracket_headers.pop(brk_index)
                brackets.pop(brk_index)
            else:
                bracket_tuples.append((brackets[brk_index], bracket_headers[brk_index][0].wrapped_element.text))
                brk_index += 1
    return bracket_tuples


def get_bracket_matches(season_title, team_dict, bracket_tuples, matches):
    header_ct = 0
    for bracket, bracket_header in bracket_tuples:
        games = bracket.find_elements_by_class_name("bracket-game")
        for game in games:
            playing_teams = game.find_elements_by_class_name("team-template-text")
            scores = game.find_elements_by_class_name("bracket-score")
            team1 = team_dict[playing_teams[0].wrapped_element.text]
            team2 = team_dict[playing_teams[3].wrapped_element.text]
            if not scores[0].wrapped_element.text == "W" and not scores[0].wrapped_element.text == "FF":
                for num in range(int(scores[0].wrapped_element.text)):
                    matches.append(Match(team1=team1, team2=team2, victor=team2,
                                         season_title=season_title, event=bracket_header))
                for num in range(int(scores[1].wrapped_element.text)):
                    matches.append(Match(team1=team1, team2=team2, victor=team2,
                                         season_title=season_title, event=bracket_header))

        header_ct += 1


def parse_teams(teamcards, season_title, player_dict):
    team_dict_maker = TeamDictionaryMaker({})
    for teamcard in teamcards:
        new_team = Team()
        new_team.active_season_title = season_title
        links = teamcard.find_elements_by_tag_name("a")
        new_team.name = links[0].wrapped_element.text
        new_team.players = []

        player_name = links[2].get_attribute("href").split('/')[-1]
        player_name = player_name.replace(player_name[0], player_name[0].lower(), 1)
        if player_dict.get(player_name, Player("Bad name", -1)).name == "Bad name":
            player_name = player_name.replace(player_name[0], player_name[0].upper(), 1)
        new_team.add_player(player_dict.get(player_name, player_dict.get("Unavailable")))

        player_name = links[4].get_attribute("href").split('/')[-1]
        player_name = player_name.replace(player_name[0], player_name[0].lower(), 1)
        if player_dict.get(player_name, Player("Bad name", -1)).name == "Bad name":
            player_name = player_name.replace(player_name[0], player_name[0].upper(), 1)
        new_team.add_player(player_dict.get(player_name, player_dict.get("Unavailable")))

        player_name = links[6].get_attribute("href").split('/')[-1]
        player_name = player_name.replace(player_name[0], player_name[0].lower(), 1)
        if player_dict.get(player_name, Player("Bad name", -1)).name == "Bad name":
            player_name = player_name.replace(player_name[0], player_name[0].upper(), 1)
        new_team.add_player(player_dict.get(player_name, player_dict.get("Unavailable")))

        team_dict_maker.fix_name(new_team)

    return team_dict_maker.team_dict


def parse_seasons(driver, player_dict):
    edge_ef_driver = EventFiringWebDriver(driver, LiquipediaNavListener())

    season_titles = []
    link_texts = []
    seasons = []

    # quick hack for cleaning the list... bottom of page contains redundant links!
    link_elements = edge_ef_driver.find_elements_by_partial_link_text("RLCS Season")
    for link_element in link_elements:
        if '-' in link_element.wrapped_element.text:
            # Get season title
            season_title = link_element.wrapped_element.text
            season_titles.append(season_title)
            link_texts.append(link_element.get_attribute("href"))

    season_num = 0
    for link in link_texts:
        is_final = "Finals" == season_titles[season_num].split('-')[1].strip()
        edge_ef_driver.get(link)
        time.sleep(20)

        # Get teams
        teamcards = edge_ef_driver.find_elements_by_class_name("teamcard")
        team_dict = parse_teams(teamcards, season_titles[season_num], player_dict)

        # Get matches
        matches = []
        if not is_final:
            # Group stage
            tables = edge_ef_driver.find_elements_by_class_name("matchlist table table-bordered collapsible")
            for table in tables:
                table_entries = table.find_elements_by_class_name("match-row")
                event = table.find_elements_by_tag_name("th").wrapped_element.text
                for match in table_entries:
                    team1 = team_dict.get(
                        table_entries[0].find_element_by_tag_name("span").get_attribute("data-highlightingclass"))
                    team2 = team_dict.get(
                        table_entries[3].find_element_by_tag_name("span").get_attribute("data-highlightingclass"))
                    team1_wins = table_entries[1].wrapped_element.text.lstrip()
                    team2_wins = table_entries[2].wrapped_element.text.lstrip()

                    if not team1_wins == "W" and not team1_wins == "FF":
                        for num in range(int(team1_wins)):
                            matches.append(Match(team1=team1, team2=team2, victor=team1,
                                                 season_title=season_titles[season_num], event=event))
                        for num in range(int(team2_wins)):
                            matches.append(Match(team1=team1, team2=team2, victor=team2,
                                                 season_title=season_titles[season_num], event=event))

            # Playoffs
            bracket_web_elements = edge_ef_driver.find_elements_by_class_name("bracket-column-matches")
            bracket_headers = [bracket.find_elements_by_class_name("bracket-header") for bracket in bracket_web_elements]
            if re.search(r"Season [789]", season_titles[season_num]):
                bracket_tuples = make_brackets(bracket_web_elements, bracket_headers, True)
            else:
                bracket_tuples = make_brackets(bracket_web_elements, bracket_headers, False)
            get_bracket_matches(season_titles[season_num], team_dict, bracket_tuples, matches)

        else:
            bracket_web_elements = edge_ef_driver.find_elements_by_class_name("bracket-column-matches")
            bracket_headers = [bracket.find_elements_by_class_name("bracket-header") for bracket in bracket_web_elements]

            bracket_tuples = make_brackets(bracket_web_elements, bracket_headers, False)

            get_bracket_matches(season_titles[season_num], team_dict, bracket_tuples, matches)

        season = Season(season_titles[season_num], player_dict, set(list(team_dict.values())), matches)
        seasons.append(season)
        edge_ef_driver.back()
        season_num += 1
        time.sleep(5)

    return seasons


def retrieve_player_data(driver):
    print("Retrieving data from https://octane.gg/stats/players/rlcs-career/")
    driver.get(url="https://octane.gg/stats/players/rlcs-career/")
    time.sleep(20)  # Give page time to load

    # For debugging and recollection
    try:
        with open("player_data.html", 'w') as out_file:
            out_file.writelines(driver.page_source)
    except UnicodeEncodeError as e:
        print(e.args)

    # Could have used Selenium to do this, but didn't know that at the time...
    with open("player_data.html", 'r') as in_file:
        parser = StatParserHTML()
        parser.feed(in_file.read())
        parser.close()

    return StatParserHTML.player_dict


def retrieve_season_data(driver, player_dict):
    print("Retrieving data from https://liquipedia.net/rocketleague/Rocket_League_Championship_Series...")
    driver.get(url="https://liquipedia.net/rocketleague/Rocket_League_Championship_Series")
    time.sleep(20)  # Give page time to load

    # For debugging and recollection
    try:
        with open("season_data.html", 'w') as out_file:
            out_file.writelines(driver.page_source)
    except UnicodeEncodeError as e:
        print(e.args)

    season_list = parse_seasons(driver, player_dict)

    return season_list


def main():
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    edge_driver = Edge(options=edge_options)
    edge_driver.minimize_window()

    # Connect to MySQL database
    try:
        db = MySQLdb.connect("localhost", "root", "toodles!?13", "player_game")
    except Exception as e:
        Popen(args="D:\\Programming Projects\\PersonalProjects\\RLCSChampionClassifier\\StartMySQL-C.bat")
        db = MySQLdb.connect("localhost", "root", "toodles!?13", "player_game")
    time.sleep(7)

    # Retrieve players and populate database
    player_dict = retrieve_player_data(edge_driver)
    player_dict["Unavailable"] = Player("Unavailable", -1)
    players = list(player_dict.values())
    # for player in players:
    #     player.to_database(db)

    season_list = retrieve_season_data(edge_driver, player_dict)
    for season in season_list:
        print(season.title)
        print("-------------------------------")
        for team in season.team_set:
            print(team)
        print("-------------------------------")
        season.to_database(db)


main()
