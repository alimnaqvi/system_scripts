#!/bin/bash

# while [[ -z ${USER_NAME} ]]; do
#     echo -n "Enter your username: "
#     read USER_NAME
# done

SYSTEMD_PATH_SYSTEM_LEVEL="/etc/systemd/system/"
SYSTEMD_PATH_USER_LEVEL="/home/${USER}/.config/systemd/user/"

SCRIPT_DIR="$(cd "$(dirname ${BASH_SOURCE[0]})" && pwd)"

FILES_SYSTEM_LEVEL=($(ls ${SCRIPT_DIR}/system_level/))
FILES_USER_LEVEL=($(ls ${SCRIPT_DIR}/user_level/))

# System-level
for FILE in "${FILES_SYSTEM_LEVEL[@]}"; do
    FILE_PATH="${SCRIPT_DIR}/system_level/${FILE}"
    echo "Attempting to create symlink for file ${FILE_PATH} in directory ${SYSTEMD_PATH_SYSTEM_LEVEL}"
    sudo ln -s ${FILE_PATH} "${SYSTEMD_PATH_SYSTEM_LEVEL}${FILE}"
    unset FILE_PATH
done
unset FILE

# User-level
for FILE in "${FILES_USER_LEVEL[@]}"; do
    FILE_PATH="${SCRIPT_DIR}/user_level/${FILE}"
    echo "Attempting to create symlink for file ${FILE_PATH} in directory ${SYSTEMD_PATH_USER_LEVEL}"
    ln -s ${FILE_PATH} "${SYSTEMD_PATH_USER_LEVEL}${FILE}"
    unset FILE_PATH
done
unset FILE

# daemon-reload and start for system-level
sudo systemctl daemon-reload
for FILE in "${FILES_SYSTEM_LEVEL[@]}"; do
    if [[ ${FILE} == *".timer" ]]; then
        echo "Attempting to enable service: ${FILE}"
        sudo systemctl enable --now ${FILE}
        echo "$(sudo systemctl status ${FILE})"
    fi
done
unset FILE

# daemon-reload and start for user-level
sudo systemctl daemon-reload
for FILE in "${FILES_USER_LEVEL[@]}"; do
    if [[ ${FILE} == *".timer" ]]; then
        echo "Attempting to enable service: ${FILE}"
        systemctl --user enable --now ${FILE}
        echo "$(systemctl --user status ${FILE})"
    fi
done
unset FILE
