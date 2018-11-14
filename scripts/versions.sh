#!/bin/bash
SELF_DIR="$(dirname "$0")"
source "$SELF_DIR/_common.sh"

GSCONTROL_REV=$(git -C ${GSCONTROL} rev-parse HEAD)
GSCONTROL_CHANGES_COUNT=$(git -C ${GSCONTROL} status --porcelain | wc -l)

if [ "${GSCONTROL_CHANGES_COUNT}" -ne "0" ]; then
	GSCONTROL_REV+=" (dirty)"
fi

PY_VERSION=$(python2.7 -V 2>&1)
PY_PATH=$(which python2.7)

GPREDICT_PATH=$(which gpredict)
GPREDICT_VERSION=$(dpkg -s `dpkg-query -S ${GPREDICT_PATH} | awk -F: '{print $1}'`  |  grep Version | awk '{print $2}')

OS_NAME=$(uname -a)

source ${PWSAT_GS_GNURADIO}/setup_env.sh
GRC_PATH=$(which gnuradio-companion)
GRC_VERSION=$(gnuradio-config-info -v)

GR_KISS_HASH=$(find ${PWSAT_GS_GNURADIO}/lib/python2.7/dist-packages/gr_kiss/ -iname *.py|sort|cat |md5sum | awk '{print $1}')

echo "Copy here and paste on GS info page:"
echo "-------"
echo "OS: ${OS_NAME}"
echo "GSControl directory: ${GSCONTROL}"
echo "GSControl revision: ${GSCONTROL_REV}"
echo "Python path: ${PY_PATH}"
echo "Python version: ${PY_VERSION}"
echo "GnuRadio path ${GRC_PATH}"
echo "GnuRadio version ${GRC_VERSION}"
echo "gr-kiss checksum ${GR_KISS_HASH}"
echo "GPredict path: ${GPREDICT_PATH}"
echo "GPredict version: ${GPREDICT_VERSION}"
