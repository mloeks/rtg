#!/bin/bash

TMP_DIR=/tmp/muden_backups
KEEP_BACKUPS=5
APP_NAME=$1

rm -rf ${TMP_DIR}
mkdir ${TMP_DIR}

# db
pg_dump -Fc muden_${APP_NAME} -f ${TMP_DIR}/muden_${APP_NAME}_$(date '+%d%b%y_%H%M').dump

# media folder
cp -rf /home/muden/${APP_NAME}/rtg/media ${TMP_DIR}/${APP_NAME}_media_$(date '+%d%b%y_%H%M') 2>/dev/null

cd ${TMP_DIR}
tar -czf /home/muden/backups/${APP_NAME}_backup_$(date '+%d%b%y_%H%M').tar.gz *

rm -rf ${TMP_DIR}

# only keep x newest backups to avoid too much storage space consumption
cd ~/backups
ls -tr ${APP_NAME}*.tar.gz | head -n -${KEEP_BACKUPS} | xargs rm -f

