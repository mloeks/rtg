#!/bin/bash

${HOME}/init/nginx stop

if [[ "$1" == "SET" ]];then
    echo "ENABLING maintenance mode..."
    rm -rf ${HOME}/backups/rtg_frontend_latest
    cp -rf ${HOME}/rtg/rtg_frontend ${HOME}/backups/rtg_frontend_latest
    rm -rf ${HOME}/rtg/rtg_frontend/*
    cp ${HOME}/scripts/rtg/maintenance.html ${HOME}/rtg/rtg_frontend/index.html
else
    echo "REMOVING maintenance mode, going back to normal..."
    cp -rf ${HOME}/backups/rtg_frontend_latest/* ${HOME}/rtg/rtg_frontend
fi

${HOME}/init/nginx start