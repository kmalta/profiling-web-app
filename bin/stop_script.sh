#!/bin/bash

pid=`pgrep -f "nf start"`
kill -INT $pid

pid=`pgrep -f "python_endpoint"`
kill -INT $pid

python $PROFILE_WEB_APP_HOME/bin/terminate_and_show_reservations.py terminate all /dev/null 2>&1
source delete_pyc_files.sh
