#!/bin/bash

${HOME}/init/nginx stop

if [[ "$1" == "SET" ]];then
    echo "ENABLING maintenance mode..."
    rm -rf ${HOME}/backups/rtg2016_frontend_latest
    cp -rf ${HOME}/rtg2016/rtg2016_frontend ${HOME}/backups/rtg2016_frontend_latest
    rm -rf ${HOME}/rtg2016/rtg2016_frontend/*
    cp ${HOME}/scripts/rtg2016/maintenance.html ${HOME}/rtg2016/rtg2016_frontend/index.html
else
    echo "REMOVING maintenance mode, going back to normal..."
    cp -rf ${HOME}/backups/rtg2016_frontend_latest/* ${HOME}/rtg2016/rtg2016_frontend
fi

${HOME}/init/nginx start