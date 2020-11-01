#!/bin/bash
SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

python2.7 "${GSCONTROL}/tools/satnogs_beacon_uploader/run.py" -c "${GSCONTROL}/tools/satnogs_beacon_uploader/satnogs_config.py" -u
