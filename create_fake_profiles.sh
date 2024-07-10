#!/bin/bash

source .env

docker exec -it $APP_CONTAINER python3 manage.py profilefactory