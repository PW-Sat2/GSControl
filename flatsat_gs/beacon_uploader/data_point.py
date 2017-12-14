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


def generate_data_points(timestamp, telemetry):
    tags = {
        "source": "comm",
    }

    point = _data_point(
        timestamp=timestamp,
        measurement="beacon",
        tags=tags,
        fields=_telemetry_fields(telemetry)
    )

    return [point]
