#!/bin/bash

SSH_CONN=muden@s17.wservices.ch

if [[ "$1" == "SET" ]];then
    echo "SETTING PROD password protection..."
    filename=rtg_passprotected.conf
else
    echo "REMOVING PROD password protection..."
    filename=rtg.conf
fi

ssh ${SSH_CONN} /home/muden/init/nginx stop
scp remote_scripts/nginx/sites/${filename} ${SSH_CONN}:/home/muden/nginx/conf/sites/rtg.conf
ssh ${SSH_CONN} /home/muden/init/nginx start