# Footy

![Footy Data Import Architecture](docs/images/architecture.png?raw=true "Footy Data Import Architecture")

## Componenets
- File Storage - Local file storage
- Python Script - Script to import the data. It connects with Control Redis Cache and worker nodes.
- Control Redis Cache - It stores the count of data imported for each service. It helps to avoid duplicate data sent to Kafka nodes.
- Worker Nodes - Worker nodes consist of Kafka and Redis instance. Upstash Kafka instance has limitation of 10000 messages per days. Each Redis stores the total messages sent in a day. When the limit exceeds, the next worker node is used.
- Connectors - Kafka topics connect with MongoDB and BiqQuery using the connectors. 
- Data Storage - MongoDB and BigQuery are used as data storage in the project.

## Services
- Teams
- Fixtures
- Fixture Line Ups
- Fixture Events
- Fixture Player Statistics
- Top Scorers

## Project Setup

```
git init
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Infrastructure Setup

The following are the infrastructure required for this project.
- Kafka
- Redis
- Mongo DB
- BigQuery

The kafka and redis can be set up using the below script. Api keys are required prior to executing the script.

### Secrets

Mongo DB Secret Configuration
```json
{
  "dev": {
    "hostname": "",
    "username": "",
    "password": ""
  },
  "prod": {
    "hostname": "",
    "username": "",
    "password": ""
  }
}
```

BigQuery Secret Configuration
```json
{
  "hostname": "",
  "username": "",
  "password": ""
}

```

API Secret Configuration
```json
{
  "control_cluster": {
    "key": "",
    "email": ""
  },
  "worker_cluster_1": {
    "key": "",
    "email": ""
  },
  "worker_cluster_2": {
    "key": "",
    "email": ""
  },
  "worker_cluster_3": {
    "key": "",
    "email": ""
  },
  "test_cluster": {
    "key": "",
    "email": ""
  }
}
```

Application Secret Configuration
```json
{
  "control_cluster": {
    "kafka": {
      "bootstrap_servers": "",
      "username": "",
      "password": ""
    },
    "redis": {
      "hostname": "",
      "port": 0,
      "password": ""
    }
  },
  "worker_cluster_1": {
    "kafka": {
      "bootstrap_servers": "",
      "username": "",
      "password": ""
    },
    "redis": {
      "hostname": "",
      "port": 0,
      "password": ""
    }
  },
  "worker_cluster_2": {
    "kafka": {
      "bootstrap_servers": "",
      "username": "",
      "password": ""
    },
    "redis": {
      "hostname": "",
      "port": 0,
      "password": ""
    }
  },
  "worker_cluster_3": {
    "kafka": {
      "bootstrap_servers": "",
      "username": "",
      "password": ""
    },
    "redis": {
      "hostname": "",
      "port": 0,
      "password": ""
    }
  },
  "test_cluster": {
    "kafka": {
      "bootstrap_servers": "",
      "username": "",
      "password": ""
    },
    "redis": {
      "hostname": "",
      "port": 0,
      "password": ""
    }
  }
}
```

### Create cluster, Kafka and Redis.
```bash
# This script creates following:
# Creates a new cluster
# Creates a kafka instance, topics and connectors
# Creates a redis instance
./scripts/upstash_infra_setup.sh
```

### Delete cluster
```bash
# This script deletes cluster and all available instances within it
python3 infra/resent_upstash_stack.py

```

## Environment Variables

The following scripts will add the necessary environment variables to provision the infrastructure and import data. 

```bash
# Infrastructure setup
source ./scripts/upstash_infra_env_setup.sh

# App configuration to import data
source ./scripts/upstash_infra_setup.sh
```


## Import Data Script

Shell Script
```bash
./scripts/import_data.sh season service base_file_path

Example:
./scripts/import_data.sh 2023 all /home/user/tmp

```

Alternatively, python script can be used.

```python
python3 ./app/entrypoints/cmd/main.py -season=2023 -service=all -loc=/home/user/tmp
```

Please refer to [commands.md](docs/commands.md) for additional commands.

For more information on the script,
```bash
python3 app/entrypoints/cmd/main.py -h
```

Available services are:
- teams
- fixtures
- fixture_lineups
- fixture_events
- fixture_player_stats
- top_scorers
- all (to executed all above services)

> **_NOTE:_**  Sample data files are available /app/entrypoints/tests/data.