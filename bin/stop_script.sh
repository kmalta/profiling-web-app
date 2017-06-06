#!/bin/bash

. ~/.bash_profile

kill -SIGINT $(ps aux | grep 'node' | awk '{print $2}') &> /dev/null
kill -9 $(ps aux | grep 'python_endpoint.py' | awk '{print $2}') &> /dev/null

python $PROFILE_WEB_APP_HOME/bin/terminate_and_show_reservations.py terminate all > /dev/null 2>&1
source delete_pyc_files.sh > /dev/null 2>&1

echo
echo "Stopped the Node server and Flask endpoint."
echo
