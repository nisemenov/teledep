#!/bin/bash

source .env

docker exec $APP_CONTAINER python3 manage.py create_fake_curators