#!/bin/bash
SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

# setting terminal to beeter GUI (PuTTY  hacks)
TERM="xterm-256color" 
NCURSES_NO_UTF8_ACS=1

if [[ ! -f ${SESSION_FILE} ]]; then
    if [ "$1" == "" ];
    then
        echo "Session number required."
        exit 1
    else
        SESSION=$1
    fi
else
    SESSION=$(<"${SESSION_FILE}")
fi

python2.7 "${GSCONTROL}/tools/monitor_file_download.py" -m "${MISSION}" "${SESSION}" "tcp://fp-main.gs.pw-sat.pl:7001" "tcp://elka-main.gs.pw-sat.pl:7001"