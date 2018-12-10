#!/bin/bash
SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

python2.7 "${GSCONTROL}/radio/radio_comm.py" -c "${GSCONTROL_CONFIG}" -r
