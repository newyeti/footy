
import json
import os
import requests
import sys
import logging
import time
import yaml

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.insert(0, parent_directory)

from app.core.exceptions.client_exception import ClientException

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('infra')

# Load YAML data from a file
with open('infra/kaka_cluster_config.yaml', 'r') as yaml_file:
    yaml_data = yaml_file.read()

env_data = os.path.expandvars(yaml_data)

# Parse YAML data
parsed_yaml = yaml.safe_load(env_data)

kafka_api_config = parsed_yaml['kafka_api']
kafka_api_url = kafka_api_config['uri']

kafka_clusters = kafka_api_config['cluster_configs']
kafka_topic_configs = kafka_api_config['topic_configs']
kafka_connector_configs = kafka_api_config['connector_configs']


def handle_error(response: requests.Response):
    if response.status_code == 400:
        raise ClientException(response.content.decode("utf-8"))
    elif response.status_code == 401:
        raise ClientException(json.loads(response.content))

def create_kafka_cluster(auth: tuple, data: dict) -> str:
    print(json.dumps(data))
    response = requests.post('https://api.upstash.com/v2/kafka/cluster', 
                             data=json.dumps(data), auth=auth)
    handle_error(response)
    
    response_data = json.loads(response.content)
    return response_data['cluster_id']

def get_cluster_info(auth: tuple) -> tuple:
    response = requests.get('https://api.upstash.com/v2/kafka/clusters', auth=auth)
    handle_error(response)
    response_data = json.loads(response.content)
    logging.debug(response_data)
    if response_data is not None and len(response_data) > 0:
        cluster_data = response_data[0]
        cluster_id = cluster_data['cluster_id']
        cluster_name = cluster_data['name']
        return (cluster_id, cluster_name)
    return ()

def create_kafka_topic(auth: tuple, cluster_id: str, topic_name: str) -> str:
    topics = list_kafka_topics(auth=auth, cluster_id=cluster_id)
    
    topic_name = [value for dct in topics for value in dct.values() if value == topic_name]
    
    if topic_name is not None or len(topic_name) > 0 :
        logging.info(f"Topic: {topic_name} already exists in the clustur: {cluster_id}.")
        return topic_name
    else:
        data = {
            "name": topic_name,
            "partitions": 2,
            "retention_time": 604800000,
            "retention_size": 268435456,
            "max_message_size": 1048576,
            "cleanup_policy": "delete",
            "cluster_id": cluster_id
            }
        
        response = requests.post('https://api.upstash.com/v2/kafka/topic', data=json.dumps(data), auth=auth)
        handle_error(response)
        logging.debug(response_data)
        response_data = json.loads(response.content)
        return response_data['topic_id']

    
def list_kafka_topics(auth: tuple, cluster_id: str) -> None:
    response = requests.get(f'https://api.upstash.com/v2/kafka/topics/{cluster_id}', auth=auth)
    handle_error(response=response)
    response_data = json.loads(response.content)
    logging.debug(response_data)
    return response_data

def create_kafka_connector(auth: tuple, data: dict) -> str:
    # data = {
    #     "name": "newyeti.mongo.football.teams.sink",
    #     "cluster_id": cluster_id,
    #     "properties": {
    #         "collection": "teams",
    #         "connection.uri": "mongodb+srv://cruser:vRixO98gZsIClFfA@uefa-cluster-0.rj6sj7h.mongodb.net/",
    #         "connector.class": "com.mongodb.kafka.connect.MongoSinkConnector",
    #         "database": "football",
    #         "topics": "newyeti.source.teams.v1"
    #         }
    #     }

    response = requests.post('https://api.upstash.com/v2/kafka/connector', 
                             data=json.dumps(data), auth=auth)
    handle_error(response=response)
    response_data = json.loads(response.content)
    return response_data['connector_id']
    

def get_kafka_connector(auth: tuple):
    pass

def validate_cluster(cluster: dict):
    cluster_api_key = cluster['api_key']
    cluster_api_email = cluster['email']
    cluster = cluster['cluster']
    if cluster_api_key == None or cluster_api_key == "":
        raise ClientException("ApiKey is required to access the kafka api.")
    if cluster_api_email == None or cluster_api_email == "":
        raise ClientException("Email is required to access the kafka api.")

def getAuthKey(cluster: dict) -> tuple:
    cluster_api_key = cluster['api_key']
    cluster_api_email = cluster['email']
    return (cluster_api_email, cluster_api_key)

def main():
    if kafka_clusters is not None:
        logging.error("Kafka cluster information is not available")
        return
    
    try:
        for kafka_cluster in kafka_clusters:
            validate_cluster(kafka_cluster)
            
            auth = getAuthKey(cluster=kafka_cluster)
            cluster_info = get_cluster_info(auth)
            logging.info(f"current cluster: {cluster_info}")
            
            # Create new cluster if it does not exists
            if len(cluster_info) == 0:
                cluster_id = create_kafka_cluster(auth=auth, data=kafka_cluster['cluster'])
                logging.info(f"cluster_id: {cluster_id}")
    
    except ClientException as e:
        logging.error(e)  
    
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    
    logging.info(f"Total time taken {end-start} seconds.")
