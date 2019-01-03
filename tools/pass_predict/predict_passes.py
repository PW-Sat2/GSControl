from gpredict_tle_loader import GpredictTleLoader
import predict
import argparse
import os
import imp
import datetime
import json

class Predicton:
    def __init__(self, start, end, maxElev, aosAzimuth):
        self.start = start
        self.end = end
        self.maxElev = maxElev
        self.aosAzimuth = aosAzimuth

def predict_pass(tle, qth, count):
    def makeDate(timestamp):
        return datetime.datetime.utcfromtimestamp(timestamp).replace(microsecond=0).isoformat() + '+00:00'

    predictions = []
    p = predict.transits(tle, qth)
    for _ in range(0, count):
        transit = p.next()
        start = makeDate(transit.start)
        stop = makeDate(transit.end)
        maxElev = round(transit.peak()['elevation'],2)
        aosAzimuth = transit.at(transit.start)['azimuth']
        predictions.append(Predicton(start, stop, maxElev, aosAzimuth))
        print("{}\t{}\t{}".format(start, stop, maxElev))
    return predictions

def generateSessions(predictions, minElev):
    sessions = []
    for sat_pass in predictions:
        if sat_pass.maxElev >= minElev:
            session = dict()
            session['short_description'] = "Automatic session."
            session['phase'] = "None"
            session['status'] = "auto"
            session['maximum_elevation'] = sat_pass.maxElev
            session['start_time_iso_with_zone'] = sat_pass.start
            session['stop_time_iso_with_zone'] = sat_pass.end
            session['primary'] = "elka" if (sat_pass.aosAzimuth < 90.0 or sat_pass.aosAzimuth > 270.0) else "fp"

            sessionObject = dict()
            sessionObject['Session']=session

            sessions.append(sessionObject)
    return sessions

def qthListToQth(qthlist):
    firstGs = qthlist[0]
    qth = (firstGs[0], -firstGs[1], firstGs[2])
    return qth


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', required=False,
                        help="Config file (in CMake-generated integration tests format)",
                        default=os.path.join(os.path.dirname(__file__), '../../config.py'))
    parser.add_argument('-s', '--session', required=False,
                        help="Next session number", type=int)
    parser.add_argument('-n', '--session-count', required=False,
                        help="Number of sessions to generate", default=1, type=int)
    
    args = parser.parse_args()
    imp.load_source('config', args.config)
    from config import config

    if "QTH" not in config:
        print "Ground Station location not found in config file. Exiting."
        return -1

    gpredict_path = "~/.config/GPredict/satdata/" if 'GPREDICT_PATH' not in config else config['GPREDICT_PATH']
    noradId = 43814 if 'NORAD_ID' not in config else config['NORAD_ID']
    minimum_elevation = 1 if 'MINIMUM_ELEVATION' not in config else config['MINIMUM_ELEVATION']

    qth = qthListToQth(config['QTH'])

    tleLoadter = GpredictTleLoader(gpredict_path)
    tleLines = tleLoadter.loadTle(noradId)
    predictions = predict_pass("\n".join(tleLines), qth, args.session_count)
    sessions = generateSessions(predictions, minimum_elevation)

    for s in sessions:
        print json.dumps(s, indent=4)

if __name__ == "__main__":
    main()