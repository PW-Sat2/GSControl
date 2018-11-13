#!/bin/bash
SELF_DIR="$(dirname "$0")"
source "$SELF_DIR/_common.sh"

python2.7 "${GSCONTROL}/radio/radio_comm.py" -c "${PWSAT_GS_CONFIG}"
