import logging
from pprint import pprint

from experiment_file import ExperimentFileParser
from summary.scope import session
from os import path

from utils import ensure_string


def parse_experiment(file_name):
    experiment_data = session.read_artifact(file_name, binary=True)
    experiment_data = ensure_string(experiment_data)

    cut = 0
    result = [[]]
    while len(result[0]) == 0:
        result = ExperimentFileParser.parse_partial(experiment_data)
        experiment_data = experiment_data[1:]
        cut += 1

    (basename, _) = path.splitext(file_name)

    with session.open_artifact(basename + '.txt', 'w') as output:
        for p in result[0]:
            pprint(p, output)

    unparsed_bytes = result[1]

    if len(unparsed_bytes) > 0:
        logging.warning('Unparsed bytes in experiment file {} ({} bytes)'.format(file_name, len(unparsed_bytes)))
        session.write_artifact(basename + '.unparsed', content=result[1], binary=True)

    logging.info("Parsed experiment file {}: Result entries: {}".format(
        file_name,
        len(result[0])
    ))