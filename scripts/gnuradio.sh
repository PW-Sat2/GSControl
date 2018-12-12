#!/bin/bash
SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"
source ${PWSAT_GS_GNURADIO}/setup_env.sh

GR="${PWSAT_GS_GNURADIO}"
GRC="${GSCONTROL}/gnuradio"

gnuradio-companion ${GRC}/downlink/downlink.grc ${GRC}/downlink/source/funcube_source.grc ${GRC}/uplink/uplink.grc
