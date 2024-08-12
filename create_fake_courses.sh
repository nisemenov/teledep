#!/bin/bash

source .env

ARGUMENT=${1:-100}

docker exec $APP_CONTAINER python3 manage.py create_fake_courses "$ARGUMENT"