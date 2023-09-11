db = connect(
  'mongodb+srv://<credentials>@uefa-cluster-0.rj6sj7h.mongodb.net/?appName=mongosh+1.10.5'
);

db.use("test_football")

// Create Collection
db.createCollection("teams")
db.createCollection('fixtures');
db.createCollection('fixture_events');
db.createCollection('fixture_lineups');
db.createCollection('fixture_player_stats');
db.createCollection('top_scorers');
db.createCollection('standings');

// Create Unique Index
db.teams.createIndex(
    { season: 1, league_id: 1, team_id: 1 },
    { name: "teams_pi", unique: true });

db.fixtures.createIndex(
  { season: 1, league_id: 1, fixture_id: 1 },
  { name: 'fixtures_pi', unique: true }
);

db.fixture_events.createIndex(
  {
    season: 1,
    league_id: 1,
    fixture_id: 1,
    event_date: 1,
    team_id: 1,
    player_id: 1,
  },
  {
    name: 'fixture_events_pi',
    unique: true,
  }
);

db.fixture_lineups.createIndex(
  {
    season: 1,
    league_id: 1,
    fixture_id: 1,
    event_date: 1,
    team_id: 1,
  },
  {
    name: 'fixture_lineups_pi',
    unique: true,
  }
);

db.fixture_player_stats.createIndex(
  {
    season: 1,
    league_id: 1,
    fixture_id: 1,
    event_date: 1,
    team_id: 1,
    player_id: 1,
  },
  {
    name: 'fixture_player_stats_pi',
    unique: true,
  }
);

db.top_scorers.createIndex(
  {
    season: 1,
    league_id: 1,
    fixture_id: 1,
    team_id: 1,
    player_id: 1,
  },
  {
    name: 'top_scorers_pi',
    unique: true,
  }
);

db.standings.createIndex(
  {
    season: 1,
    league_id: 1,
    team_id: 1,
  },
  {
    name: 'standings_pi',
    unique: true,
  }
);






