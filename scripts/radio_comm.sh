#!/bin/bash
SELF_DIR="$(dirname "$0")"
source "$SELF_DIR/_common.sh"

/c/Python27/python.exe "${GSCONTROL}/radio/radio_comm.py" -c "${PWSAT_GS_CONFIG}"
