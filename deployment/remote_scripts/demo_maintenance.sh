#!/bin/bash

${HOME}/init/nginx stop

if [[ "$1" == "SET" ]];then
    echo "ENABLING maintenance mode on DEMO..."
    rm -rf ${HOME}/backups/rtg_demo_frontend_latest
    cp -rf ${HOME}/rtg_demo/rtg_frontend ${HOME}/backups/rtg_demo_frontend_latest
    rm -rf ${HOME}/rtg_demo/rtg_frontend/*
    cp ${HOME}/scripts/rtg/maintenance.html ${HOME}/rtg_demo/rtg_frontend/index.html
else
    echo "REMOVING maintenance mode on DEMO, going back to normal..."
    cp -rf ${HOME}/backups/rtg_demo_frontend_latest/* ${HOME}/rtg_demo/rtg_frontend
fi

${HOME}/init/nginx start