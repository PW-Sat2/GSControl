#!/bin/bash
SELF_DIR="$(dirname "$0")"
source "$SELF_DIR/_common.sh"

GR="${PWSAT_GS_GNURADIO}"
GRC="${GSCONTROL}/gnuradio"

source ${GR}/setup_env.sh
gnuradio-companion ${GRC}/downlink/downlink.grc ${GRC}/downlink/source/funcube_source.grc ${GRC}/uplink/uplink-fp.grc
