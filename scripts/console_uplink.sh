#!/bin/bash
SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

if [[ ! -f ${SESSION_FILE} ]]; then
    echo "Session not running. "
    exit 1
fi
SESSION=$(<"${SESSION_FILE}")


python2.7 "${GSCONTROL}/radio/radio_comm.py" -c "${GSCONTROL_CONFIG}" -s "${SESSION}"
