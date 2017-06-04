#!/bin/bash

pid=`pgrep -f "nf start"`
kill -INT $pid

pid=`pgrep -f "python_endpoint"`
kill -INT $pid

source scripts_to_run_locally/delete_pyc_files.sh
python scripts_to_run_locally/terminate_and_show_reservations.py terminate all
