#!/bin/bash
SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

python2.7 "${GSCONTROL}/tools/grafana_beacon_uploader/run.py" -d http://grafana.pw-sat.pl:8086/pwsat2 --gs=${GS_NAME}
