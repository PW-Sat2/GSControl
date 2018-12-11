SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
GSCONTROL="$(dirname $( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd ))"
REPOS="$(dirname ${GSCONTROL})"
MISSION="${REPOS}/mission"
SESSION_FILE="/gs/current_session.lock"

echo "Using PW-Sat2 REPOS at $REPOS"

GSCONTROL_CONFIG=/gs/config.py
GNURADIO_CONFIG=/gs/gr_config

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

confirm() {
    # call with a prompt string or use a default
    read -r -p "${1} Are you sure you want to continue? [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}
