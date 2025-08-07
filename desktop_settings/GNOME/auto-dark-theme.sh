#!/bin/bash

CURRENT_HOUR=$(date +%H)

# Remove leading zero as it would make bash think it is octal
# `#pattern` removes the first shortest match from start
CURRENT_HOUR=${CURRENT_HOUR#0}

if [[ ${CURRENT_HOUR} -ge 6 && ${CURRENT_HOUR} -lt 20 ]]; then
    COLOR_SCHEME="prefer-light"
    GTK_THEME="Pop"
else
    COLOR_SCHEME="prefer-dark"
    GTK_THEME="Pop-dark"
fi

gsettings set org.gnome.desktop.interface color-scheme "${COLOR_SCHEME}"
gsettings set org.gnome.desktop.interface gtk-theme "${GTK_THEME}"
