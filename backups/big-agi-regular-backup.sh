#!/bin/bash

DOWNLOADS_DIR=~/Downloads/
BACKUP_DIR=~/my_projects/LLMs/big-AGI-backups/

for FILE in ${DOWNLOADS_DIR}backup_chats*; do

    FILE_BASE=$(basename ${FILE})

    # Rename file to add current hostname for better identification
    FILE_BASE_HOST=$(echo "${FILE_BASE}" | sed "s/backup_chats/backup_chats_$(uname -n)/g") \
    && echo "Renamed ${FILE_BASE} to ${FILE_BASE_HOST}"

    if [[ -f "${BACKUP_DIR}${FILE_BASE_HOST}" ]]; then
        echo "Skipping file ${FILE_BASE_HOST} because it already exists in ${BACKUP_DIR}."
        continue
    fi

    echo "Attempting to copy ${FILE} to ${BACKUP_DIR}${FILE_BASE_HOST}"
    cp ${FILE} "${BACKUP_DIR}${FILE_BASE_HOST}"

done \
&& cd ${BACKUP_DIR} && git add . && git commit -m "regular backup" && git push && echo "Successfully finished big-agi-regular-backup"
