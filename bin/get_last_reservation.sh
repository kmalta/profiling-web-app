#!/bin/bash
. ~/.bash_profile
LAST_DIR=$(ls -t $PROFILE_WEB_APP_HOME/profiles | head -1)
PATH_ELEMS=(${LAST_DIR//\// })

LENGTH=${#PATH_ELEMS[@]}
LAST_POSITION=$((LENGTH - 1))
LAST_PART=${PATH_ELEMS[${LAST_POSITION}]}

echo $LAST_PART
