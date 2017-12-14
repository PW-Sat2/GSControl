from datetime import timedelta


def _build_key(group, field):
    group = group[4:]
    field = field[6:]
    return group + "." + field


def _decode_value(o):
    if isinstance(o, timedelta):
        return o.total_seconds()

    try:
        return _decode_value(o.converted)
    except AttributeError:
        return o


def _data_point(timestamp, measurement, fields, tags):
    return {
        "measurement": measurement,
        "tags": tags,
        "time": timestamp.isoformat(),
        "fields": fields
    }


def _telemetry_fields(telemetry):
    fields = {}

    for group in telemetry:
        for field in telemetry[group]:
            key = _build_key(group, field)

            fields[key] = _decode_value(telemetry[group][field])

    return fields


def _error_counter_data_points(timestamp, telemetry):
    points = []

    error_counters = telemetry['04: Error Counters']

    for device in error_counters:
        key = device[6:]

        points.append(_data_point(
            timestamp=timestamp,
            measurement='error_counters',
            tags={
                "counter": key
            },
            fields={
                "value": error_counters[device]
            }
        ))

    return points


def _lcl_data_points(timestamp, telemetry):
    points = []

    lcls = {
        "TKmain": 1 << 0,
        "SunS": 1 << 1,
        "CamNadir": 1 << 2,
        "CamWing": 1 << 3,
        "SENS": 1 << 4,
        "Antenna": 1 << 5,
        "IMTQ": 1 << 6,
    }

    state = telemetry['14: Controller A']['1006: DISTR.LCL_STATE']
    flag_b = telemetry['14: Controller A']['1013: DISTR.LCL_FLAGS']

    for lcl in lcls:
        mask = lcls[lcl]

        points.append(_data_point(
            timestamp=timestamp,
            measurement="lcl",
            tags={
                "lcl": lcl
            },
            fields={
                "enabled": (state & mask) == mask,
                "flag_b": (flag_b & mask) == mask
            }
        ))

    return points


def generate_data_points(timestamp, telemetry):
    tags = {
        "source": "comm",
    }

    telemetry_point = [_data_point(
        timestamp=timestamp,
        measurement="beacon",
        tags=tags,
        fields=_telemetry_fields(telemetry)
    )]

    error_counters = _error_counter_data_points(timestamp, telemetry)

    lcl = _lcl_data_points(timestamp, telemetry)

    points = telemetry_point + error_counters + lcl

    for p in points:
        p['tags'].update(tags)

    return points
