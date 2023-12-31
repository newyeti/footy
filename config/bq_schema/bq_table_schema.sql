CREATE TABLE `newyeti.football.fixture_player_stats`
(
  season INT64,
  league_id INT64,
  fixture_id INT64,
  event_date TIMESTAMP,
  player_id INT64,
  player_name STRING,
  team_id INT64,
  team_name STRING,
  number INT64,
  position STRING,
  rating FLOAT64,
  minutes_played INT64,
  caption STRING,
  substitute INT64,
  offsides INT64,
  shots STRUCT<total INT64, `on` INT64>,
  goals STRUCT<total INT64, conceded INT64, assists INT64, saves INT64>,
  passes STRUCT<total INT64, key INT64, accuracy INT64>,
  tackles STRUCT<total INT64, blocks INT64, interceptions INT64>,
  duels STRUCT<total INT64, won INT64>,
  dribbles STRUCT<attempts INT64, success INT64, past INT64>,
  fouls STRUCT<drawn INT64, committed INT64>,
  cards STRUCT<yellow INT64, red INT64>,
  penalty STRUCT<won INT64, committed INT64, success INT64, saved INT64>
)
PARTITION BY TIMESTAMP_TRUNC(event_date, YEAR)
CLUSTER BY season, league_id, fixture_id, player_id;

CREATE TABLE `newyeti.football.fixture_lineups`
(
  season INT64,
  league_id INT64,
  fixture_id INT64,
  event_date TIMESTAMP,
  coach_id INT64,
  coach_name STRING,
  formation STRING,
  team_id INT64,
  startingXI ARRAY<STRUCT<player_id INT64, player_name STRING>>,
  substitutes ARRAY<STRUCT<player_id INT64, player_name STRING>>
)
PARTITION BY TIMESTAMP_TRUNC(event_date, MONTH)
CLUSTER BY season, league_id, fixture_id;

CREATE TABLE `newyeti.football.top_scorers`
(
  season INT64,
  league_id INT64,
  player_id INT64,
  player_name STRING,
  firstname STRING,
  lastname STRING,
  position STRING,
  nationality STRING,
  team_id INT64,
  team_name STRING,
  games STRUCT<appearences INT64, minutes_played INT64>,
  goals STRUCT<total INT64, assists INT64, conceded INT64, saves INT64>,
  shots STRUCT<total INT64, `on` INT64>,
  penalty STRUCT<won INT64, committed INT64>,
  cards STRUCT<yellow INT64, second_yellow INT64, red INT64>
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2010, 2050, 10))
CLUSTER BY season, league_id;

CREATE TABLE `newyeti.football.fixture_events`
(
  season INT64,
  event_date TIMESTAMP,
  league_id INT64,
  fixture_id INT64,
  elapsed INT64,
  elapsed_plus INT64,
  team_id INT64,
  team_name STRING,
  player_id INT64,
  player_name STRING,
  assist_player_id INT64,
  assist_player_name STRING,
  event_type STRING,
  detail STRING,
  comments STRING
)
PARTITION BY TIMESTAMP_TRUNC(event_date, MONTH)
CLUSTER BY season, league_id, fixture_id;

CREATE TABLE `newyeti.football.teams`
(
  season INT64,
  league_id INT64,
  team_id INT64,
  name STRING,
  code STRING,
  founded INT64,
  stadium_capacity INT64,
  stadium_surface STRING,
  street STRING,
  city STRING,
  country STRING,
  is_national BOOL
)
PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2010, 2050, 10))
CLUSTER BY season, league_id, team_id;

CREATE TABLE `newyeti.football.fixtures`
(
  season INT64,
  league_id INT64,
  fixture_id INT64,
  league_name STRING,
  event_date TIMESTAMP,
  first_half_start STRING,
  second_half_start STRING,
  round STRING,
  status STRING,
  elapsed INT64,
  stadium STRING,
  referee STRING,
  home_team STRUCT<team_id INT64, team_name STRING, team_logo STRING>,
  away_team STRUCT<team_id INT64, team_name STRING, team_logo STRING>,
  goals STRUCT<home_team INT64, away_team INT64>,
  score STRUCT<half_time STRING, full_time STRING, extra_time STRING, penalty STRING>
)
PARTITION BY TIMESTAMP_TRUNC(event_date, YEAR)
CLUSTER BY season, league_id;

ALTER TABLE `newyeti.football.teams` ADD PRIMARY KEY (season, league_id, team_id) NOT ENFORCED;
ALTER TABLE `newyeti.football.fixtures` ADD PRIMARY KEY (season, league_id, fixture_id) NOT ENFORCED;
ALTER TABLE `newyeti.football.fixture_events` ADD PRIMARY KEY (season, league_id, fixture_id) NOT ENFORCED;
ALTER TABLE `newyeti.football.fixture_lineups` ADD PRIMARY KEY (season, league_id, fixture_id, team_id) NOT ENFORCED;
ALTER TABLE `newyeti.football.fixture_player_stats` ADD PRIMARY KEY (season, league_id, fixture_id, team_id, player_id, event_date) NOT ENFORCED;
ALTER TABLE `newyeti.football.top_scorers` ADD PRIMARY KEY (season, league_id, player_id) NOT ENFORCED;
