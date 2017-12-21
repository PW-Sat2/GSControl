import unittest

from datetime import datetime

from telemetry import determine_files_timespan, FileView, TelemetryView, MAX_TELEMETRY_IN_FILE, chunks_count, \
    TELEMETRY_INTERVAL, MAX_FILE_TIME_SPAN


class TelemetryFilesCalculatorTest(unittest.TestCase):
    def test_parse_file_list_to_telemetry_view(self):
        file_list = [
            ('telemetry.current', 12 * 230),
            ('telemetry.previous', 512 * 1024)
        ]

        timestamp = datetime(2017, 4, 30, 23, 0, 0)

        result = determine_files_timespan(file_list, timestamp)

        self.assertValidTelemetryView(result)

    def test_file_view_calc(self):
        ts = datetime(2017, 4, 30, 23, 0, 0)
        result = FileView(ts, 1)

        self.assertEqual(result.timestamp, ts)
        self.assertEqual(result.chunks, 1)
        self.assertEqual(result.last_entry, ts)
        self.assertEqual(result.first_entry, datetime(2017, 4, 30, 23, 0, 0))

    def test_estimate_telemetry_no_overflow(self):
        timestamp = datetime(2017, 4, 30, 23, 0, 0)

        base_view = TelemetryView(timestamp, 100, MAX_TELEMETRY_IN_FILE)

        next_timestamp = datetime(2017, 4, 30, 23, 30, 0)

        estimated = base_view.estimate_at(next_timestamp)

        self.assertValidTelemetryView(estimated)

        self.assertEqual(estimated.current_file_view.chunks, 100 + 60)
        self.assertEqual(estimated.previous_file_view.chunks, MAX_TELEMETRY_IN_FILE)

    def test_estimate_telemetry_overflow_current_to_previous(self):
        timestamp = datetime(2017, 4, 30, 23, 0, 0)

        base_view = TelemetryView(timestamp, 100, MAX_TELEMETRY_IN_FILE)

        next_timestamp = datetime(2017, 5, 1, 23, 0, 0)

        estimated = base_view.estimate_at(next_timestamp)

        self.assertValidTelemetryView(estimated)

        self.assertEqual(estimated.current_file_view.chunks, 701)
        self.assertEqual(estimated.previous_file_view.chunks, MAX_TELEMETRY_IN_FILE)

        self.assertEqual(estimated.current_file_view.last_entry, next_timestamp)
        self.assertEqual(estimated.current_file_view.first_entry, datetime(2017, 5, 1, 17, 10, 0))

        self.assertEqual(estimated.previous_file_view.last_entry, datetime(2017, 5, 1, 17, 9, 30))
        self.assertEqual(estimated.previous_file_view.first_entry, datetime(2017, 4, 30, 22, 10, 30))

    def test_estimate_telemetry_double_overflow(self):
        timestamp = datetime(2017, 4, 30, 23, 0, 0)

        base_view = TelemetryView(timestamp, 100, MAX_TELEMETRY_IN_FILE)

        next_timestamp = datetime(2017, 5, 2, 23, 0, 0)

        estimated = base_view.estimate_at(next_timestamp)

        self.assertValidTelemetryView(estimated)

        self.assertEqual(estimated.current_file_view.chunks, 1302)
        self.assertEqual(estimated.previous_file_view.chunks, MAX_TELEMETRY_IN_FILE)

        self.assertEqual(estimated.current_file_view.last_entry, next_timestamp)
        self.assertEqual(estimated.current_file_view.first_entry, datetime(2017, 5, 2, 12, 9, 30))

        self.assertEqual(estimated.previous_file_view.last_entry, datetime(2017, 5, 2, 12, 9, 0))
        self.assertEqual(estimated.previous_file_view.first_entry, datetime(2017, 5, 1, 17, 10, 0))

    def test_chunks_count(self):
        self.assertEqual(chunks_count(0), 0)
        self.assertEqual(chunks_count(229), 1)
        self.assertEqual(chunks_count(230 + 230 + 230 + 229), 4)
        self.assertEqual(chunks_count(512 * 1024), MAX_TELEMETRY_IN_FILE)

    def assertValidTelemetryView(self, view):
        self.assertLess(view.current_file_view.first_entry, view.current_file_view.last_entry)
        self.assertLess(view.previous_file_view.last_entry, view.current_file_view.first_entry)
        self.assertLess(view.previous_file_view.first_entry, view.previous_file_view.last_entry)
        self.assertEqual(view.previous_file_view.chunks, MAX_TELEMETRY_IN_FILE)

        self.assertEqual(view.current_file_view.first_entry - view.previous_file_view.last_entry, TELEMETRY_INTERVAL)

        self.assertEqual(view.previous_file_view.last_entry - view.previous_file_view.first_entry, MAX_FILE_TIME_SPAN)