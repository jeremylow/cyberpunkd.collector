#!/bin/bash

NAME="cyberpunkd" # Name of the application
DJANGODIR=/home/jeremy/servers/cyberpunkd/cyberpunkd
VENVDIR=/home/jeremy/Envs/cyberpunkd
PORT=8585

USER=jeremy # the user to run as
GROUP=jeremy # the group to run as
NUM_WORKERS=22 # how many worker processes should Gunicorn spawn

 # which settings file should Django use
DJANGO_SETTINGS_MODULE=cyberpunkd.settings
DJANGO_WSGI_MODULE=cyberpunkd.wsgi # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source $VENVDIR/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec $VENVDIR/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --log-level=info \
    --bind=127.0.0.1:$PORT

