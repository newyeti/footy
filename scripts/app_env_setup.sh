#!/bin/sh

infra_credentials=`gcloud secrets versions access latest --secret=upstash_infra_credentials`

get_infra_credentials() {
    json_key=$1
    echo $( jq -r  $json_key <<< "${infra_credentials}" )
}

echo "Setting up application envrionment variables"

# Application envrionment variables

export CSV_FILE_PATH=/Users/sachindra.maharjan/Documents/pl/leagueID_696

#Application
export NEWYETI_TEST_CLIENT_ID=newyeti_test_client
export NEWYETI_TEST_REDIS_HOST=$(get_infra_credentials '.test_cluster.redis.hostname')
export NEWYETI_TEST_REDIS_PORT=$(get_infra_credentials '.test_cluster.redis.port')
export NEWYETI_TEST_REDIS_PASSWORD=$(get_infra_credentials '.test_cluster.redis.password')
export NEWYETI_TEST_REDIS_SSL_ENABLED=TRUE
export NEWYETI_TEST_KAFKA_BOOTSTRAP_SERVERS=$(get_infra_credentials '.test_cluster.kafka.bootstrap_servers')
export NEWYETI_TEST_KAFKA_USERNAME=$(get_infra_credentials '.test_cluster.kafka.username')
export NEWYETI_TEST_KAFKA_PASSWORD=$(get_infra_credentials '.test_cluster.kafka.password')

export NEWYETI_WORKER1_CLIENT_ID=newyeti_worker1_client
export NEWYETI_WORKER1_REDIS_HOST=$(get_infra_credentials '.worker_cluster_1.redis.hostname')
export NEWYETI_WORKER1_REDIS_PORT=$(get_infra_credentials '.worker_cluster_1.redis.port')
export NEWYETI_WORKER1_REDIS_PASSWORD=$(get_infra_credentials '.worker_cluster_1.redis.password')
export NEWYETI_WORKER1_REDIS_SSL_ENABLED=TRUE
export NEWYETI_WORKER1_KAFKA_BOOTSTRAP_SERVERS=$(get_infra_credentials '.worker_cluster_1.kafka.bootstrap_servers')
export NEWYETI_WORKER1_KAFKA_USERNAME=$(get_infra_credentials '.worker_cluster_1.kafka.username')
export NEWYETI_WORKER1_KAFKA_PASSWORD=$(get_infra_credentials '.worker_cluster_1.kafka.password')

export NEWYETI_WORKER2_CLIENT_ID=newyeti_worker2_client
export NEWYETI_WORKER2_REDIS_HOST=$(get_infra_credentials '.worker_cluster_2.redis.hostname')
export NEWYETI_WORKER2_REDIS_PORT=$(get_infra_credentials '.worker_cluster_2.redis.port')
export NEWYETI_WORKER2_REDIS_PASSWORD=$(get_infra_credentials '.worker_cluster_2.redis.password')
export NEWYETI_WORKER2_REDIS_SSL_ENABLED=TRUE
export NEWYETI_WORKER2_KAFKA_BOOTSTRAP_SERVERS=$(get_infra_credentials '.worker_cluster_2.kafka.bootstrap_servers')
export NEWYETI_WORKER2_KAFKA_USERNAME=$(get_infra_credentials '.worker_cluster_2.kafka.username')
export NEWYETI_WORKER2_KAFKA_PASSWORD=$(get_infra_credentials '.worker_cluster_2.kafka.password')

export NEWYETI_WORKER3_CLIENT_ID=newyeti_worker3_client
export NEWYETI_WORKER3_REDIS_HOST=$(get_infra_credentials '.worker_cluster_3.redis.hostname')
export NEWYETI_WORKER3_REDIS_PORT=$(get_infra_credentials '.worker_cluster_3.redis.port')
export NEWYETI_WORKER3_REDIS_PASSWORD=$(get_infra_credentials '.worker_cluster_3.redis.password')
export NEWYETI_WORKER3_REDIS_SSL_ENABLED=TRUE
export NEWYETI_WORKER3_KAFKA_BOOTSTRAP_SERVERS=$(get_infra_credentials '.worker_cluster_3.kafka.bootstrap_servers')
export NEWYETI_WORKER3_KAFKA_USERNAME=$(get_infra_credentials '.worker_cluster_3.kafka.username')
export NEWYETI_WORKER3_KAFKA_PASSWORD=$(get_infra_credentials '.worker_cluster_3.kafka.password')

#control
export NEWYETI_CONTROL_CLIENT_ID=newyeti-control_client
export NEWYETI_CONTROL_REDIS_HOST=$(get_infra_credentials '.control_cluster.redis.hostname')
export NEWYETI_CONTROL_REDIS_PORT=$(get_infra_credentials '.control_cluster.redis.port')
export NEWYETI_CONTROL_REDIS_PASSWORD=$(get_infra_credentials '.control_cluster.redis.password')
export NEWYETI_CONTROL_REDIS_SSL_ENABLED=TRUE
export NEWYETI_CONTROL_KAFKA_BOOTSTRAP_SERVERS=$(get_infra_credentials '.control_cluster.kafka.bootstrap_servers')
export NEWYETI_CONTROL_KAFKA_USERNAME=$(get_infra_credentials '.control_cluster.kafka.username')
export NEWYETI_CONTROL_KAFKA_PASSWORD=$(get_infra_credentials '.control_cluster.kafka.password')


echo "Finished setting up application envrionment variables"