#!/bin/sh

season=$1
service=$2
filepath=$3

source ./scripts/app_env_setup.sh 

python3 app/entrypoints/cmd/main.py -season $season -service $service -loc $filepath

echo "Data import completed!!!"
