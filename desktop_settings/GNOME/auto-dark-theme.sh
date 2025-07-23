#!/bin/bash

CURRENT_HOUR=$(date +%H)

if [[ ${CURRENT_HOUR} -ge 6 && ${CURRENT_HOUR} -lt 20 ]]; then
    THEME="light"
else
    THEME="dark"
fi

gsettings set org.gnome.desktop.interface color-scheme "prefer-${THEME}"
gsettings set org.gnome.desktop.interface gtk-theme "Pop-${THEME}"
