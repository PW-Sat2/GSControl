import logging
from summary import telemetry_file_mapper
from summary.scope import session, influx
from os import path

from tools.grafana_beacon_uploader.data_point import generate_data_points


def load_telemetry_file(file_name):
    logging.info('Load telemetry file {}'.format(file_name))
    file_raw = session.read_artifact(file_name, binary=True)

    entries = telemetry_file_mapper.read_telemetry_buffer(file_raw)

    entry_mapping = telemetry_file_mapper.map_telemetry(influx, entries)

    tags = {
        'ground_station': 'telemetry-archive',
        'import_marker': '{}-session-{}'.format(path.basename(file_name), session.session_number)
    }

    all_points = []

    for item in entry_mapping:
        item_points = generate_data_points(item.db_timestamp, item.telemetry_item, tags)
        all_points += item_points

    print 'Total {} points'.format(len(all_points))

    influx.write_points(all_points)
