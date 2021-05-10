#!/usr/bin/env bash

# copies contents of ./remote_scripts to ~/scripts/rtg on DjangoEurope server.

SSH_CON=muden@s17.wservices.ch

scp -r remote_scripts/* ${SSH_CON}:/home/muden/scripts/rtg/

ssh ${SSH_CON} cp -rf /home/muden/scripts/rtg/nginx/sites/* /home/muden/nginx/conf/sites
ssh ${SSH_CON} cp -rf /home/muden/scripts/rtg/init/* /home/muden/init

# remove conflicting passprotected conf, which should only overwrite PROD config in emergencies
ssh ${SSH_CON} rm -f /home/muden/nginx/conf/sites/rtg_passprotected.conf
