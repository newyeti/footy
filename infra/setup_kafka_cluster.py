
import json
import os
import requests
import sys

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.insert(0, parent_directory)

from app.core.exceptions.client_exception import ClientException

def handle_error(response: requests.Response):
    if response.status_code == 400:
        raise ClientException(response.content.decode("utf-8"))
    elif response.status_code == 401:
        raise ClientException(json.loads(response.content))

def create_kafka_cluster(auth: tuple) -> str:
    data = '{"name":"newyeti-prod-cluster1","region":"us-east-1","multizone":true}'
    response = requests.post('https://api.upstash.com/v2/kafka/cluster', data=data, auth=auth)
    handle_error(response)
    
    response_data = json.loads(response.content)
    return response_data['cluster_id']

def get_cluster_id(auth: tuple) -> str:
    response = requests.get('https://api.upstash.com/v2/kafka/clusters', auth=auth)
    handle_error(response)
    response_data = json.loads(response.content)
    if response_data is not None and len(response_data) > 0:
        cluster_data = response_data[0]
        cluster_id = cluster_data['cluster_id']
        return cluster_id
    return ""

def create_kafka_topic(auth: tuple, cluster_id: str, topic_name: str) -> str:
    data = {
        "name": topic_name,
        "partitions": 1,
        "retention_time": 1234,
        "retention_size": 4567,
        "max_message_size": 8912,
        "cleanup_policy": "delete",
        "cluster_id": cluster_id
        }
    
    response = requests.post('https://api.upstash.com/v2/kafka/topic', data=json.dumps(data), auth=auth)
    handle_error(response)
    response_data = json.loads(response.content)
    print(response_data)
    return ""
    
def list_kafka_topics(auth: tuple, cluster_id: str) -> None:
    pass

def create_kafka_connector(auth: tuple):
    pass

def get_kafka_connector(auth: tuple):
    pass

def main():
    api_key = os.environ['UPSTASH_API_KEY']
    email =  os.environ['EMAIL_ADDRESS']
    auth=(email, api_key)
    
    try:
        cluster_id = get_cluster_id(auth)
        if cluster_id is None or cluster_id == "":
            cluster_id = create_kafka_cluster()
        print(f"cluster_id: {cluster_id}")
        
        create_kafka_topic(auth=auth, cluster_id=cluster_id, topic_name="newyeti.source.teams.v1")
        
        
    except ClientException as e:
        print(e)

if __name__ == "__main__":
    main()
