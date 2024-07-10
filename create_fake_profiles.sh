#!/bin/bash

source .env

docker exec $APP_CONTAINER python3 manage.py profilefactory