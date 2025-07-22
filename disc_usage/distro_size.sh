#!/bin/bash

NUM_ARGS=$#

# Define the log file path
LOG_FILE="/var/log/distro_disk_usage.log"

# Get the current date and time in ISO 8601 format
TIMESTAMP=$(date --iso-8601=seconds)

get_disk_usage() {
    DISK_USAGE_GB=$(sudo du -sh --exclude=/mnt / 2>/dev/null | cut -f1) 
}

log_disk_usage() {
    # Create header row if file doesn't exist or is 0 bytes
    if [[ ! -e ${LOG_FILE} || ! -s ${LOG_FILE} ]]; then
        sudo echo "Timestamp,Disk usage (GB),Message" > "${LOG_FILE}"
        echo "Added header row to log file"
    fi

    sudo echo "${TIMESTAMP},${DISK_USAGE_GB},${MESSAGE}" >> "${LOG_FILE}"
    echo "Logged distro size of ${DISK_USAGE_GB} to the log file ${LOG_FILE}"
}

if [[ NUM_ARGS -eq 0 ]]; then
    echo "Please provide an argument. Possible arguments:
    --check, -c
        check and display the current size (without logging)
    --show, -s
        show the entire log file
    --log, -l
        log the current size to log file ${LOG_FILE}
    --message, -m
        add a message for logging. Argument only allowed with --log"
    exit
# Else will only execute if any arguments were provided
else
    if [[ NUM_ARGS -gt 1 ]]; then
        if [[ $1 != "--log" && $1 != "-l" ]]; then
            echo "Invalid number of arguments."
            exit 1
        fi
    fi

    if [[ $1 == "--check" || $1 == "-c" ]]; then
        # check and display the current size (without logging)
        echo "Calculating disk usage (this may take a while)..."
        get_disk_usage
        echo "Distro size is currently ${DISK_USAGE_GB}"
        exit
    
    elif [[ $1 == "--show" || $1 == "-s" ]]; then
        # show the entire log file, if it exists and is not empty
        if [[ ! -e ${LOG_FILE} ]]; then
            echo "Log file does not exist"
            exit 1
        fi

        if [[ ! -s ${LOG_FILE} ]]; then
            echo "(Log file is empty)"
        fi

        sudo column -t -s, ${LOG_FILE}
        exit

    elif [[ $1 == "--log" || $1 == "-l" ]]; then
        # log the current size to log file; handle optional message
        if [[ NUM_ARGS -gt 1 ]]; then
            if [[ $2 != "--message" && $2 != "-m" ]]; then
                echo "Unkown argument: $2"
                exit 1
            fi

            if [[ NUM_ARGS -ne 3 ]]; then
                echo "Please provide the log message as one argument."
                exit 1
            fi

            MESSAGE=$3
        fi

        echo "Calculating disk usage (this may take a while)..."
        get_disk_usage
        log_disk_usage

    elif [[ $1 == "--cron" || $1 == "--systemd" ]]; then
        # script was called by cron/systemd (run at reboot); log only if no log on this day
        CURRENT_DATE=$(date +%Y-%m-%d)
        LAST_RUN_DATE=$(cat ${LOG_FILE} | tail --lines 1 | cut -c1-10)
        MESSAGE="logged by ${1:2}" # remove first two characters (hyphens)

        if [[ CURRENT_DATE != LAST_RUN_DATE ]]; then
            echo "Logging disk usage with cron/systemd" # not required but no harm in leaving it in
            get_disk_usage
            log_disk_usage
        fi

        exit

    else
        echo "Unknown argument: $1"
        exit 1
    fi

fi
