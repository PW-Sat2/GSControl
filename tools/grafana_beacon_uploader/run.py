import sys
import colorlog
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '../../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

if os.getenv("CLICOLOR_FORCE") == "1":
    print "Forcing colors"
    import colorama

    colorama.deinit()


def _setup_log(silent):
    root_logger = logging.getLogger()

    handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)-15s %(levelname)s: [%(name)s] %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    handler.setFormatter(formatter)

    root_logger.addHandler(handler)

    if silent:
        root_logger.setLevel(logging.INFO)
    else:
        root_logger.setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


from app import BeaconUploaderApp
args = BeaconUploaderApp.parse_args(sys.argv[1:])
_setup_log(args.silent)

BeaconUploaderApp.main_with_args_parsed(args)
