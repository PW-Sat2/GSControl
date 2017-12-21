from datetime import timedelta

import math

TELEMETRY_INTERVAL = timedelta(seconds=30)
MAX_TELEMETRY_IN_FILE = 1 + (512 * 1024 - 299) / 230
MAX_FILE_TIME_SPAN = (MAX_TELEMETRY_IN_FILE - 1) * TELEMETRY_INTERVAL


def chunks_count(size):
    aligned_chunks = size / 230
    rem = size % 230

    if rem == 229:
        return aligned_chunks + 1
    else:
        return aligned_chunks + 0


class FileView(object):
    def __init__(self, timestamp, chunks):
        self.timestamp = timestamp
        self.chunks = chunks
        self.last_entry = timestamp
        self.first_entry = timestamp - (chunks - 1) * TELEMETRY_INTERVAL

    def __repr__(self):
        return '{} -> {}'.format(self.first_entry, self.last_entry)


class TelemetryView(object):
    def __init__(self, timestamp, current_chunks, previous_chunks):
        self.timestamp = timestamp
        self.current_file_view = FileView(timestamp, current_chunks)
        self.previous_file_view = FileView(self.current_file_view.first_entry - TELEMETRY_INTERVAL, previous_chunks)

    def estimate_at(self, asof):
        assert asof > self.timestamp, "Estimation can only happen for dates in future"

        time_increment = asof - self.timestamp
        new_chunks = int(math.ceil(time_increment.total_seconds() / TELEMETRY_INTERVAL.total_seconds()))

        if self.current_file_view.chunks + new_chunks > MAX_TELEMETRY_IN_FILE:
            overflow = (self.current_file_view.chunks + new_chunks) % MAX_TELEMETRY_IN_FILE

            return TelemetryView(asof, overflow, MAX_TELEMETRY_IN_FILE)

        return TelemetryView(asof, self.current_file_view.chunks + new_chunks, self.previous_file_view.chunks)


def determine_files_timespan(file_list, file_list_time):
    files = dict(file_list)

    current_chunks = chunks_count(files['telemetry.current'])
    previous_chunks = chunks_count(files['telemetry.previous'])

    view = TelemetryView(file_list_time, current_chunks, previous_chunks)

    return view


__all__ = [
    'FileView',
    'TelemetryView',
    'TELEMETRY_INTERVAL',
    'MAX_FILE_TIME_SPAN',
    'MAX_TELEMETRY_IN_FILE',
    'chunks_count'
]