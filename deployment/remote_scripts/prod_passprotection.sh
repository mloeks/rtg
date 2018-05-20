#!/bin/bash

if [[ "$1" == "SET" ]];then
    echo "SETTING PROD password protection..."
    CONF_FILE=${HOME}/scripts/rtg/rtg_passprotected.conf

else
    echo "REMOVING PROD password protection..."
    CONF_FILE=${HOME}/scripts/rtg/rtg.original.conf
fi

${HOME}/init/nginx stop

cd ${HOME}/nginx/conf/sites/
cp ${CONF_FILE} ./rtg.conf

${HOME}/init/nginx start