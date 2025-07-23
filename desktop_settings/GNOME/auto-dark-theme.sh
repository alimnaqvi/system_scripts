#!/bin/bash

CURRENT_HOUR=$(date +%H)

if [[ ${CURRENT_HOUR} -ge 6 && ${CURRENT_HOUR} -lt 20 ]]; then
    THEME="prefer-light"
else
    THEME="prefer-dark"
fi

gsettings set org.gnome.desktop.interface color-scheme ${THEME}
