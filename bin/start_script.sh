#!/bin/bash

. ~/.bash_profile
source delete_pyc_files.sh > /dev/null 2>&1
python $PROFILE_WEB_APP_HOME/bin/terminate_and_show_reservations.py terminate all > /dev/null 2>&1

python $PROFILE_WEB_APP_HOME/flask_endpoint_scripts/python_endpoint.py >> server_logs/flask_endpoint.log 2>&1 &
nf --procfile $PROFILE_WEB_APP_HOME/node_src/Procfile start >> server_logs/node_web_app.log 2>&1 &

echo
echo "Node server and Flask endpoint starting..."
echo
echo "Node server logging set to $PROFILE_WEB_APP_HOME/server_logs/node_web_app.log"
echo "Flask endpoint logging set to $PROFILE_WEB_APP_HOME/server_logs/flask_endpoint.log"
