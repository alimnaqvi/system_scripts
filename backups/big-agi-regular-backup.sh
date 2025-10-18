#!/bin/bash

DOWNLOADS_DIR=~/Downloads/
BACKUP_DIR=~/my_projects/LLMs/big-AGI-backups/
TO_BACK_UP=(${DOWNLOADS_DIR}backup_chats*)

if [[ ${#TO_BACK_UP[@]} -gt 1 ]]; then
    echo "${DOWNLOADS_DIR} contains more than one file. Please ensure there is only one file to back up"
    exit 1
fi

FILE=${TO_BACK_UP[0]}

FILE_BASE=$(basename ${FILE})

# Rename file to add current hostname for better identification
FILE_BASE_HOST=$(echo "${FILE_BASE}" | sed "s/backup_chats/backup_chats_$(uname -n)/g")

if [[ -f "${BACKUP_DIR}${FILE_BASE_HOST}" ]]; then
    echo "Skipping file ${FILE_BASE_HOST} because it already exists in ${BACKUP_DIR}"
    exit
fi

OLD_FILES=(${BACKUP_DIR}backup_chats*)
if [[ -f ${OLD_FILES[0]} ]]; then
    echo "Deleting previous backups in ${BACKUP_DIR}"
    gio trash ${BACKUP_DIR}backup_chats*
fi

echo "Attempting to copy ${FILE} to ${BACKUP_DIR}${FILE_BASE_HOST}"
cp ${FILE} "${BACKUP_DIR}${FILE_BASE_HOST}" \
&& cd ${BACKUP_DIR} && git add . && git commit -m "regular backup" && git push && echo "Successfully finished big-agi-regular-backup"
