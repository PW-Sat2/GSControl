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

def _temperate_data_points(timestamp, telemetry):
    points = []

    temperatures = [
        ('10: Gyroscope', '0558: Temperature', 'Gyroscope', 'Temperature'),
        ('11: Comm', '0605: [Last transmission] Power Amplifier Temperature', 'COMM', '[Last transmission] PA Temperature'),
        ('11: Comm', '0744: [Now] Oscillator Temperature', 'COMM', '[Now] Oscillator Temperature'),
        ('11: Comm', '0756: [Now] Power Amplifier Temperature', 'COMM', '[Now] PA Temperature'),
        ('13: MCU', '0781: Temperature', 'MCU', 'Temperature'),
        ('14: Controller A', '0829: MPPT_X.Temperature', 'EPS Controller A', 'MPPT_X'),
        ('14: Controller A', '0880: MPPT_Y+.Temperature', 'EPS Controller A', 'MPPT_Y+'),
        ('14: Controller A', '0931: MPPT_Y-.Temperature', 'EPS Controller A', 'MPPT_Y-'),
        ('14: Controller A', '1049: BATC.Temperature', 'EPS Controller A', 'BATC'),
        ('14: Controller A', '1062: BP.Temperature A', 'EPS Controller A', 'BP A'),
        ('14: Controller A', '1075: BP.Temperature B', 'EPS Controller A', 'BP B'),
        ('14: Controller A', '1144: Temperature', 'EPS Controller A', 'Temperature'),
        ('14: Controller A', '1154: SUPP_TEMP', 'EPS Controller A', 'SUPP_TEMP'),
        ('14: Controller A', '1174: DCDC3V3.Temperature', 'EPS Controller A', 'DCDC 3V3'),
        ('14: Controller A', '1184: DCDC5V.Temperature', 'EPS Controller A', 'DCDC 5V'),
        ('15: Controller B', '1194: BP.Temperature', 'EPS Controller B', 'BP'),
        ('15: Controller B', '1270: Temperature', 'EPS Controller B', 'Temperature'),
        ('15: Controller B', '1280: SUPP_TEMP', 'EPS Controller B', 'SUPP_TEMP'),
        ('20: Imtq Housekeeping', '1605: MCU Temperature', 'IMTQ', 'MCU Temperature'),
        ('22: Imtq Temperature', '1669: Coil Temperature 1', 'IMTQ', 'Coil 1'),
        ('22: Imtq Temperature', '1685: Coil Temperature 2', 'IMTQ', 'Coil 2'),
        ('22: Imtq Temperature', '1701: Coil Temperature 3', 'IMTQ', 'Coil 3'),
    ]

    for (group, field, device, sensor) in temperatures:
        points.append(_data_point(
            timestamp=timestamp,
            measurement="temperatures",
            tags={
                "device": device,
                'sensor': sensor
            },
            fields={
                "value": float(telemetry[group][field].converted)
            }
        ))

    return points

def generate_data_points(timestamp, telemetry, extra_tags):
    tags = {
        "source": "comm",
    }

    tags.update(extra_tags)

    telemetry_point = [_data_point(
        timestamp=timestamp,
        measurement="beacon",
        tags=tags,
        fields=_telemetry_fields(telemetry)
    )]

    error_counters = _error_counter_data_points(timestamp, telemetry)
    lcl = _lcl_data_points(timestamp, telemetry)
    temperatures = _temperate_data_points(timestamp, telemetry)

    points = telemetry_point + error_counters + lcl + temperatures

    for p in points:
        p['tags'].update(tags)

    return points
