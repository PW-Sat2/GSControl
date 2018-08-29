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


def _setup_log():
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
    root_logger.setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


_setup_log()

from app import BeaconUploaderApp

BeaconUploaderApp.main(sys.argv[1:])
