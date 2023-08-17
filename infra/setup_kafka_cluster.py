
import json
import os
import requests
import sys

# Add the parent directory (app) to sys.path
current_directory =  os.path.abspath(os.path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, ".."))
sys.path.insert(0, parent_directory)

from app.core.exceptions.client_exception import ClientException

api_key = os.environ['UPSTASH_API_KEY']
email =  os.environ['EMAIL_ADDRESS']

def create_kafka_cluster() -> str:
    data = '{"name":"newyeti-prod-cluster1","region":"us-east-1","multizone":true}'
    response = requests.post('https://api.upstash.com/v2/kafka/cluster', data=data, auth=(email, api_key))
    if response.status_code == 400:
        raise ClientException(response.content)
    
    response_data = json.loads(response.content)
    return response_data['cluster_id']

def get_cluster_id() -> str:
    response = requests.get('https://api.upstash.com/v2/kafka/clusters', auth=(email, api_key))
    response_data = json.loads(response.content)
    if response_data is not None and len(response_data) > 0:
        cluster_data = response_data[0]
        cluster_id = cluster_data['cluster_id']
        return cluster_id
    return ""

def create_kafka_topic():
    pass

def list_kafka_topics():
    pass

def create_kafka_connector():
    pass

def get_kafka_connector():
    pass

def main():
    try:
        cluster_id = get_cluster_id()
        if cluster_id is None or cluster_id == "":
            cluster_id = create_kafka_cluster()
        print(f"cluster_id: {cluster_id}")
    except ClientException as e:
        print(e)

if __name__ == "__main__":
    main()