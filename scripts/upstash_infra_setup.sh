#!/bin/sh

source ./scripts/upstash_infra_env_setup.sh

python3 infra/provision_upstash_stack.py

echo "Upstash infrastructure provision completed!!!"
