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

GSCONTROL_CONFIG=/gs/config.py
GNURADIO_CONFIG=/gs/gr_config

confirm_ask() {
    # call with a prompt string or use a default
    read -r -p "${1} [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}

confirm() {
    confirm_ask "${1} Are you sure you want to continue?"
}
