#!/bin/bash

source .env

docker stop $APP_CONTAINER
docker exec $POSTGRES_CONTAINER psql -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;" -p $DB_PORT
docker exec $POSTGRES_CONTAINER psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;" -p $DB_PORT
docker start $APP_CONTAINER
