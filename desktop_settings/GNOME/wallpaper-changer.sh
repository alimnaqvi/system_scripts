#!/bin/bash

WALLPAPER_DIR=/home/ali/Pictures/desktop_wallpapers
CURRENT_THEME=$(gsettings get org.gnome.desktop.interface color-scheme)

# Check whether we are changing dark theme wallpaper or light theme one
if [[ ${CURRENT_THEME} == *"dark"* ]]; then
    THEME_DIR="${WALLPAPER_DIR}/dark/"
    KEY_TO_CHANGE="picture-uri-dark"
elif [[ ${CURRENT_THEME} == *"light"* ]]; then
    THEME_DIR="${WALLPAPER_DIR}/light/"
    KEY_TO_CHANGE="picture-uri"
else
    exit # do nothing if color-scheme is set to 'default'
fi

WALLPAPER_LIST=(${THEME_DIR}*)
NUM_WALLPAPERS=${#WALLPAPER_LIST[@]}

# Generate a random number between 0 and (NUM_WALLPAPERS - 1)
RAND_NUM=$(($RANDOM % ${NUM_WALLPAPERS}))

# Set the relevant gsettings key to a random picture within relevant directory
FILE_VALUE="file://${WALLPAPER_LIST[RAND_NUM]}"
echo "attempting to set wallpaper: ${FILE_VALUE}"
gsettings set org.gnome.desktop.background ${KEY_TO_CHANGE} "${FILE_VALUE}"
