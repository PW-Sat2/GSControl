import unittest

from datetime import datetime, timedelta

from hypothesis import given
import hypothesis.strategies as st

from telemetry import determine_files_timespan, FileView, TelemetryView, MAX_TELEMETRY_IN_FILE, chunks_count, \
    TELEMETRY_INTERVAL, MAX_FILE_TIME_SPAN


@st.composite
def telemetry_file_data(draw, stamp=st.datetimes(), chunks=st.integers(min_value=1, max_value=MAX_TELEMETRY_IN_FILE)):
    return draw(stamp), draw(chunks)


@st.composite
def estimation_data(draw, base=telemetry_file_data()):
    (stamp, chunks) = draw(base)
    next_stamp = draw(st.datetimes(min_value=stamp + timedelta(seconds=1)))

    return stamp, chunks, next_stamp


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
        self.assertLessEqual(view.current_file_view.first_entry, view.current_file_view.last_entry, "Current: first < last")
        self.assertLess(view.previous_file_view.last_entry, view.current_file_view.first_entry, "Current: first < last")
        self.assertLess(view.previous_file_view.first_entry, view.previous_file_view.last_entry, "Previous last < current first")
        self.assertEqual(view.previous_file_view.chunks, MAX_TELEMETRY_IN_FILE, "Previous is full")

        self.assertEqual(view.current_file_view.first_entry - view.previous_file_view.last_entry, TELEMETRY_INTERVAL, "30 seconds between last previous and first current")

        self.assertEqual(view.previous_file_view.last_entry - view.previous_file_view.first_entry, MAX_FILE_TIME_SPAN, "previous spans over maximum time")

    # @given(stamp=st.datetimes(), current_chunks=st.integers(min_value=1, max_value=MAX_TELEMETRY_IN_FILE))
    @given(telemetry_file_data())
    def test_construct_valid_telemetry_view_from_chunks_count_and_timestamp(self, args):
        (stamp, current_chunks) = args

        view = TelemetryView(stamp, current_chunks, MAX_TELEMETRY_IN_FILE)

        self.assertValidTelemetryView(view)

    @given(estimation_data())
    def test_estimate_valid_telemetry_view(self, args):
        stamp, current_chunks, next_stamp = args

        view = TelemetryView(stamp, current_chunks, MAX_TELEMETRY_IN_FILE)

        next_view = view.estimate_at(next_stamp)

        self.assertValidTelemetryView(next_view)

