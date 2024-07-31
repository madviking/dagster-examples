#!/bin/bash

# simple shell script for setting up the hosts file
# so Dagster can communicate with our Docker containers
# that are running REST APIs

NGINX=${APP_ENV}_nginx_container

IP_ADDRESS=$(nslookup ${NGINX} | grep "Address:" | awk '{print $2}' | sed -n '2p')
echo "Queried IP: ${IP_ADDRESS}"

echo -e "\n# Hosts for the services\n" >> /etc/hosts
echo "${IP_ADDRESS} ${SERVER_1}" >> /etc/hosts
echo "${IP_ADDRESS} ${SERVER_2}" >> /etc/hosts
echo "${IP_ADDRESS} ${SERVER_3}" >> /etc/hosts

# test
curl ${SERVER_1}

exec "$@"
