#!/bin/bash

LOG_FILE="/var/log/capslock-fix.log"

echo "----------------------------------" >> ${LOG_FILE}
echo "The script $0 ran at $(date +%c)" >> ${LOG_FILE}
echo "Value of DISPLAY environment variable is: $DISPLAY" >> ${LOG_FILE}

exit_with_log() {
	echo "$2" >> ${LOG_FILE}
	echo "----------------------------------" >> ${LOG_FILE}
	exit $1
}

if [[ -z "$DISPLAY" ]]; then
    exit_with_log 1 "DISPLAY environment variable does not have a value"
fi

xkbcomp -xkb "$DISPLAY" - | sed 's#key <CAPS>.*#key <CAPS> {\
    repeat=no,\
    type[group1]="ALPHABETIC",\
    symbols[group1]=[ Caps_Lock, Caps_Lock],\
    actions[group1]=[ LockMods(modifiers=Lock),\
    Private(type=3,data[0]=1,data[1]=3,data[2]=3)]\
};\
#' | xkbcomp -w 0 - "$DISPLAY"

exit_with_log 0 "Keyboard mapping changed successfully"
