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

def _gyro_data_points(timestamp, telemetry):
    points = []

    gyro = telemetry['10: Gyroscope']

    for field in ['0510: X measurement', '0526: Y measurement', '0542: Z measurement']:
        axis = field[6]    
        points.append(_data_point(
            timestamp=timestamp,
            measurement="gyroscope",
            tags={
                "axis": axis
            },
            fields={
                "value": float(gyro[field].converted)
            }
        ))

    return points

def _mppt_data_points(timestamp, telemetry):
    points = []

    ctrl_a = telemetry['14: Controller A']

    mppts = [
        ('X', '0793: MPPT_X.SOL_VOLT', '0805: MPPT_X.SOL_CURR', '0817: MPPT_X.SOL_OUT_VOLT', '0829: MPPT_X.Temperature','0841: MPPT_X.State'),
        ('Y+', '0844: MPPT_Y+.SOL_VOLT', '0856: MPPT_Y+.SOL_CURR', '0868: MPPT_Y+.SOL_OUT_VOLT', '0880: MPPT_Y+.Temperature', '0892: MPPT_Y+.State'),
        ('Y-', '0895: MPPT_Y-.SOL_VOLT','0907: MPPT_Y-.SOL_CURR','0919: MPPT_Y-.SOL_OUT_VOLT','0931: MPPT_Y-.Temperature','0943: MPPT_Y-.State')
    ]

    for (name, volt, curr, out_volt, temp, state) in mppts:
        points.append(_data_point(
            timestamp=timestamp,
            measurement="mppt",
            tags={
                "name": name
            },
            fields={
                "voltage": float(ctrl_a[volt].converted),
                "current": float(ctrl_a[curr].converted),
                "out_voltage": float(ctrl_a[out_volt].converted),
                "temperature": float(ctrl_a[temp].converted),
                "state": int(ctrl_a[state]),
            }
        ))

    return points

def _eps_dist_data_points(timestamp, telemetry):
    points = []

    sensors = [
        ('3V3', '14: Controller A', '0946: DISTR.VOLT_3V3', '0956: DISTR.CURR_3V3'),
        ('5V', '14: Controller A', '0966: DISTR.VOLT_5V', '0976: DISTR.CURR_5V'),
        ('VBAT', '14: Controller A', '0986: DISTR.VOLT_VBAT', '0996: DISTR.CURR_VBAT'),
        ('BATC (A)', '14: Controller A', '1019: BATC.VOLT_A', None),
        ('BATC (B)', '15: Controller B', '1204: BATC.VOLT_B', None),
        ('BATC Charging', '14: Controller A', None, '1029: BATC.CHRG_CURR'),
        ('BATC Discharging', '14: Controller A', None, '1039: BATC.DCHRG_CURR'),
        ('EPS B', '14: Controller A', None, '1164: ControllerB.3V3d'),
        ('EPS A', '15: Controller B', None, '1290: ControllerA.3V3d'),
    ]

    for (name, group, volt, curr) in sensors:
        fields = {}
        if volt is not None:
            fields['voltage'] = float(telemetry[group][volt].converted)
        if curr is not None:
            fields['current'] = float(telemetry[group][curr].converted)

        points.append(_data_point(
            timestamp=timestamp,
            measurement="distribution",
            tags={
                "name": name
            },
            fields=fields
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
    gyro = _gyro_data_points(timestamp, telemetry)
    mppt = _mppt_data_points(timestamp, telemetry)
    dist = _eps_dist_data_points(timestamp, telemetry)

    points = telemetry_point + error_counters + lcl + temperatures + gyro + mppt + dist

    for p in points:
        p['tags'].update(tags)

    return points


def generate_deep_sleep_data_points(timestamp, telemetry, extra_tags):
    tags = {
        "source": "comm",
    }

    tags.update(extra_tags)

    telemetry_point = [_data_point(
        timestamp=timestamp,
        measurement="deep_beacon",
        tags=tags,
        fields=_telemetry_fields(telemetry)
    )]

    points = telemetry_point

    for p in points:
        p['tags'].update(tags)

    return points
