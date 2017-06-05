#!/bin/bash

LAST_DIR=$(ls -t profiles | head -1)
PATH_ELEMS=(${LAST_DIR//\// })

LENGTH=${#PATH_ELEMS[@]}
LAST_POSITION=$((LENGTH - 1))
LAST_PART=${PATH_ELEMS[${LAST_POSITION}]}

echo $LAST_PART
