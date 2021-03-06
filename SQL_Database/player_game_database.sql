SET GLOBAL sql_mode = ANSI;

CREATE TABLE player
(
NAME VARCHAR(30) PRIMARY KEY,	
ID INT,
WIN_PERC float,
GAMES_PLAYED INT,
SCPG INT,
GPG INT,
APG INT,
SAPG INT,
SHPG INT,
TOT_SCORE INT,
TOT_GOALS INT,
TOT_ASSISTS INT,
TOT_SAVES INT,
TOT_SHOTS INT,
TOT_HT INT,
TOT_SAVIOR INT,
TOT_PM INT,
TOT_MVP INT,
SC_PERC_OF_TEAM FLOAT,
G_PERC_OF_TEAM FLOAT,
A_PERC_OF_TEAM FLOAT,
SA_PERC_OF_TEAM FLOAT,
SH_PERC_OF_TEAM FLOAT,
AVG_SCB_POS FLOAT,
ASSIST_GOAL_RATIO FLOAT,
SH_PERC FLOAT,
GOAL_PART FLOAT
);

DROP TABLE team;

CREATE TABLE team
(
NAME VARCHAR(50),
ACTIVE_SEASON_TITLE VARCHAR(50),
TEAM_MEMBER_1 VARCHAR(30),
TEAM_MEMBER_2 VARCHAR(30),
TEAM_MEMBER_3 VARCHAR(30),
PRIMARY KEY(NAME, ACTIVE_SEASON_TITLE),
CONSTRAINT fk_player1 FOREIGN KEY(TEAM_MEMBER_1) REFERENCES player(NAME) ON UPDATE CASCADE,
CONSTRAINT fk_player2 FOREIGN KEY(TEAM_MEMBER_2) REFERENCES player(NAME) ON UPDATE CASCADE,
CONSTRAINT fk_player3 FOREIGN KEY(TEAM_MEMBER_3) REFERENCES player(NAME) ON UPDATE CASCADE
);


CREATE TABLE `match`
(
ID INT PRIMARY KEY,
TEAM_1 VARCHAR(50),
TEAM_2 VARCHAR(50),
VICTOR VARCHAR(50),
SEASON_TITLE VARCHAR(80),
`EVENT` VARCHAR(50),
CONSTRAINT fk_team1 FOREIGN KEY(TEAM_1, SEASON_TITLE) REFERENCES team(NAME, ACTIVE_SEASON_TITLE) ON UPDATE CASCADE,
CONSTRAINT fk_team2 FOREIGN KEY(TEAM_2, SEASON_TITLE) REFERENCES team(NAME, ACTIVE_SEASON_TITLE) ON UPDATE CASCADE,
CONSTRAINT fk_victor FOREIGN KEY(VICTOR, SEASON_TITLE) REFERENCES team(NAME, ACTIVE_SEASON_TITLE) ON UPDATE CASCADE
);
