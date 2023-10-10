#!/bin/sh

upstash_cluster_api_keys=`gcloud secrets versions access latest --secret=upstash_cluster_api_keys`
mongo_credentials=`gcloud secrets versions access latest --secret=newyeti_mongo_credentials`
bq_credentials=`gcloud secrets versions access latest --secret=newyeti_bq_credentials`

upstash_cluster_api_keys() {
    json_key=$1
    echo $( jq -r  $json_key <<< "${upstash_cluster_api_keys}" )
}

get_mongo_credentials() {
    json_key=$1
    echo $( jq -r  $json_key <<< "${mongo_credentials}" )
}

echo $(upstash_cluster_api_keys '.dev.key')
echo $(upstash_cluster_api_keys ".dev.email")

echo "Setting up application envrionment variables"

# API Keys
export NEWYETI_CONTROL_KEY=$(upstash_cluster_api_keys '.control_cluster.key')
export NEWYETI_CONTROL_EMAIL=$(upstash_cluster_api_keys ".control_cluster.email")

export NEWYETI_WORKER_CLUSTER1_KEY=$(upstash_cluster_api_keys '.worker_cluster_1.key')
export NEWYETI_WORKER_CLUSTER1_EMAIL=$(upstash_cluster_api_keys ".worker_cluster_1.email")

export NEWYETI_WORKER_CLUSTER2_KEY=$(upstash_cluster_api_keys '.worker_cluster_2.key')
export NEWYETI_WORKER_CLUSTER2_EMAIL=$(upstash_cluster_api_keys ".worker_cluster_2.email")

export NEWYETI_WORKER_CLUSTER3_KEY=$(upstash_cluster_api_keys '.worker_cluster_3.key')
export NEWYETI_WORKER_CLUSTER3_EMAIL=$(upstash_cluster_api_keys ".worker_cluster_3.email")

export NEWYETI_DEV_KEY=$(upstash_cluster_api_keys '.dev.key')
export NEWYETI_DEV_EMAIL=$(upstash_cluster_api_keys ".dev.email")

# Database
export MONGO_HOSTNAME=$(get_mongo_credentials '.prod.hostname')
export MONGO_USERNAME=$(get_mongo_credentials '.prod.username')
export MONGO_PASSWORD=$(get_mongo_credentials '.prod.password')
export MONGO_USERNAME_TEST=$(get_mongo_credentials '.dev.username')
export MONGO_PASSWORD_TEST=$(get_mongo_credentials '.dev.password')

export BIGQUERY_CREDENTIALS=${bq_credentials}

echo "Finished setting up application envrionment variables"