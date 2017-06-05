#!/bin/bash

pid=`pgrep -f "nf start"`
kill -INT $pid

pid=`pgrep -f "python_endpoint"`
kill -INT $pid

source delete_pyc_files.sh
python terminate_and_show_reservations.py terminate all
