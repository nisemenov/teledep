#!/bin/bash

source .env

docker exec -it $APP_CONTAINER python3 manage.py migrate
docker exec $APP_CONTAINER python3 manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
docker exec $APP_CONTAINER python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); user.set_password('$DJANGO_SUPERUSER_PASSWORD'); user.save()"
