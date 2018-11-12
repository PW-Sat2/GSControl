
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
GSCONTROL="$(dirname $( cd -P "$( dirname "$SOURCE" )" >/dev/null && pwd ))"

echo "Using GSControl at $GSCONTROL"

if [ ! -f ${PWSAT_GS_CONFIG} ]; then
	echo "Config file '${PWSAT_GS_CONFIG}' not found"
	exit 1
fi

if [ ! -d ${PWSAT_GS_GNURADIO} ]; then
	echo "GnuRadio directory '${PWSAT_GS_GNURADIO}' not found"
	exit 1
fi
