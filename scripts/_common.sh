SELF_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source "$SELF_DIR/_common_functions.sh"

if [[ ! -f ${GSCONTROL_CONFIG} ]]; then
	echo "Config file '${GSCONTROL_CONFIG}' not found"
	exit 1
fi

if [[ ! -f ${GNURADIO_CONFIG} ]]; then
	echo "GNU Radio Config file '${GNURADIO_CONFIG}' not found"
	exit 1
fi

if [[ ! -d ${PWSAT_GS_GNURADIO} ]]; then
	echo "GnuRadio directory '${PWSAT_GS_GNURADIO}' not found"
	exit 1
fi

if [[ -z ${GS_NAME} ]]; then
	echo "GS name not defined"
	exit 1
fi

source ${PWSAT_GS_GNURADIO}/setup_env.sh
