import argparse
from urlparse import urlparse

from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

import matplotlib.pyplot as plt
from lookup_extractor import FloatLookupExporter
from lookup_loader import FloatLookupLoader

import time, datetime

INFLUX_QUERY = """
SELECT "Controller A.BATC.VOLT_A", "Controller B.BATC.VOLT_B", "Controller A.MPPT_X.SOL_VOLT", "Controller A.MPPT_Y+.SOL_VOLT", "Controller A.MPPT_Y-.SOL_VOLT", "Controller A.BATC.DCHRG_CURR" FROM beacon WHERE "Controller A.BATC.VOLT_A" > 6
"""

class InputDataSet:
    def __init__(self, time=[],
                       batc_vbat_a=[],
                       batc_vbat_b=[],
                       batc_dchrg_curr = [],
                       mppt_x_sol_volt=[],
                       mppt_yp_sol_volt=[],
                       mppt_yn_sol_volt=[]):
        self.time = time
        self.batc_vbat_a = batc_vbat_a
        self.batc_vbat_b = batc_vbat_b
        self.batc_dchrg_curr = batc_dchrg_curr
        self.mppt_x_sol_volt = mppt_x_sol_volt
        self.mppt_yp_sol_volt = mppt_yp_sol_volt
        self.mppt_yn_sol_volt = mppt_yn_sol_volt


def query_beacons(influx_url, influxdb_query):
    url = urlparse(influx_url)
    db = InfluxDBClient(host=url.hostname, port=url.port, database=url.path.strip('/'))

    result = db.query(influxdb_query)
    return result.get_points('beacon')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("influx", help="InfluxDB URL (http://<serve>:<port>/<database>")
    return parser.parse_args()


def main(args):
    print("Generating BP lookup table...")
    lookup_exporter = FloatLookupExporter()
    lookup_exporter.save_to_file("bp_discharge_20deg.csv")

    bp_discharge_lookup = FloatLookupLoader("bp_discharge_20deg.csv")

    print("Downloading beacons from Grafana...")
    beacons = query_beacons(args.influx, INFLUX_QUERY)
    data_set = InputDataSet()

    for beacon in beacons:
        data_set.time.append(beacon['time'])
        data_set.batc_vbat_a.append(beacon['Controller A.BATC.VOLT_A'])
        data_set.batc_vbat_b.append(beacon['Controller B.BATC.VOLT_B'])
        data_set.batc_dchrg_curr.append(beacon['Controller A.BATC.DCHRG_CURR'])
        data_set.mppt_x_sol_volt.append(beacon['Controller A.MPPT_X.SOL_VOLT'])
        data_set.mppt_yp_sol_volt.append(beacon['Controller A.MPPT_Y+.SOL_VOLT'])
        data_set.mppt_yn_sol_volt.append(beacon['Controller A.MPPT_Y-.SOL_VOLT'])

    print("Generating charts...")

    energy = []
    batc_vbat_a_filtered = []
    mission_durations = []

    for index in range(0, len(data_set.batc_vbat_a)):
        if data_set.batc_dchrg_curr[index] < 0.15 and data_set.mppt_x_sol_volt[index] < 0.2 and data_set.mppt_yp_sol_volt[index] < 0.2 and data_set.mppt_yn_sol_volt[index] < 0.2:
            energy.append(bp_discharge_lookup.to_wh(data_set.batc_vbat_a[index]))
            batc_vbat_a_filtered.append(data_set.batc_vbat_a[index])
        else:
            energy.append(None)
            batc_vbat_a_filtered.append(None)

        year = int(data_set.time[index].split("T")[0].split("-")[0])
        month =  int(data_set.time[index].split("T")[0].split("-")[1])
        day = int(data_set.time[index].split("T")[0].split("-")[2])
        hour = int(data_set.time[index].split("T")[1].split(":")[0])
        minute = int(data_set.time[index].split("T")[1].split(":")[0])
        mission_durations.append(round((datetime.datetime(year, month, day, hour, minute) - datetime.datetime(2018, 12, 4, 1, 5)).total_seconds()/86400.0, 3))

    ax1 = plt.subplot(211)
    ax1.plot(mission_durations, energy, 'g', label='Calculated energy')
    plt.title("Calculated energy (points imported from Grafana)")
    plt.ylabel("Energy [Wh]")
    plt.legend()

    ax2 = plt.subplot(212, sharex=ax1)
    ax2.plot(mission_durations, data_set.batc_vbat_a, 'b', label='Raw BATC.VBAT_A')
    ax2.hold(True)
    ax2.plot(mission_durations, batc_vbat_a_filtered, 'r.', label='Filtered BATC.VBAT_A')
    plt.title("VBAT_A and filtered points")
    plt.xlabel("Mission day (Grafana time)")
    plt.ylabel("Voltage [V]")
    plt.legend()

    plt.show()

main(parse_args())
