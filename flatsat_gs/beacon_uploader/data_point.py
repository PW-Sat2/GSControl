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
                # "source": "comm",
                "counter": key
            },
            fields={
                "value": error_counters[device]
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

    points = telemetry_point + error_counters

    for p in points:
        p['tags'].update(tags)

    return points
