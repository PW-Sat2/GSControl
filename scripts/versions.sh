#!/bin/bash
SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common.sh"

GSCONTROL_REV=$(git -C ${GSCONTROL} rev-parse HEAD)
GSCONTROL_MASTER_REV=$(git -C ${GSCONTROL} rev-parse origin/master)
GSCONTROL_CHANGES_COUNT=$(git -C ${GSCONTROL} status --porcelain | wc -l)

MISSION_REV=$(git -C ${MISSION} rev-parse HEAD)
MISSION_MASTER_REV=$(git -C ${MISSION} rev-parse origin/master)
MISSION_CHANGES_COUNT=$(git -C ${MISSION} status --porcelain | wc -l)

echo ${MISSION_MASTER_REV}
if [[ "${GSCONTROL_CHANGES_COUNT}" -ne "0" ]]; then
	GSCONTROL_REV+=" (dirty)"
fi

if [[ "${MISSION_CHANGES_COUNT}" -ne "0" ]]; then
	MISSION_REV+=" (dirty)"
fi

PY_VERSION=$(python2.7 -V 2>&1)
PY_PATH=$(which python2.7)

GPREDICT_PATH=$(which gpredict)
GPREDICT_VERSION=$(dpkg -s `dpkg-query -S ${GPREDICT_PATH} | awk -F: '{print $1}'`  |  grep Version | awk '{print $2}')

OS_NAME=$(uname -a)

GRC_PATH=$(which gnuradio-companion)
GRC_VERSION=$(gnuradio-config-info -v)

GR_KISS_HASH=$(find ${PWSAT_GS_GNURADIO}/lib/python2.7/dist-packages/gr_kiss/ -iname *.py|sort|cat |md5sum | awk '{print $1}')

echo "GS Name: ${GS_NAME}"
echo "OS: ${OS_NAME}"
echo "GSControl directory: ${GSCONTROL}"
echo "GSControl revision: ${GSCONTROL_REV}"
echo "Mission directory: ${MISSION}"
echo "Mission revision: ${MISSION_REV}"
echo "Python path: ${PY_PATH}"
echo "Python version: ${PY_VERSION}"
echo "GnuRadio path ${GRC_PATH}"
echo "GnuRadio version ${GRC_VERSION}"
echo "gr-kiss checksum ${GR_KISS_HASH}"
echo "GPredict path: ${GPREDICT_PATH}"
echo "GPredict version: ${GPREDICT_VERSION}"
