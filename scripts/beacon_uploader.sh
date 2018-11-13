#!/bin/bash
SELF_DIR="$(dirname "$0")"
source "$SELF_DIR/_common.sh"

python2.7 "${GSCONTROL}/tools/grafana_beacon_uploader/run.py" -d http://grafana.pw-sat.pl:8086/pwsat2 --gs=${PWSAT_GS_NAME}
