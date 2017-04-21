#!/bin/bash

if [[ "$1" == "SET" ]];then
    echo "SETTING PROD password protection..."
    CONF_FILE=${HOME}/scripts/rtg2016/rtg2016_passprotected.conf

else
    echo "REMOVING PROD password protection..."
    CONF_FILE=${HOME}/scripts/rtg2016/rtg2016_original.conf
fi

${HOME}/init/nginx stop

cd ${HOME}/nginx/conf/sites/
cp ${CONF_FILE} ./rtg2016.conf

${HOME}/init/nginx start