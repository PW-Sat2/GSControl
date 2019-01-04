from gpredict_tle_loader import GpredictTleLoader
from prediction import Predicton
import predict
import argparse
import os
import imp
import datetime
import json
from collections import OrderedDict

def predict_pass(tle, qths, count):
    def predictOneStation(tle, qth):
        predictions = []
        p = predict.transits(tle, qth)
        for _ in range(0, count):
            transit = p.next()
            start = transit.start
            stop = transit.end
            maxElev = round(transit.peak()['elevation'],2)
            aosAzimuth = transit.at(transit.start)['azimuth']

            prediction = Predicton(start, stop, maxElev, aosAzimuth)          
            predictions.append(prediction)
            
        return predictions
   
    allStationPredictions = []
    for station in qths:
        allStationPredictions.append(predictOneStation(tle,station))       

    return allStationPredictions

def mergeStationPredictions(allStationPredictions):
    def comparisonFunction(element1, element2):
        diff = abs(element1.start - element2.start)
        return diff < 20 * 60
    
    def groupSimilarPasses(allPredictions):
        groupped = []
        visited = []
        for prediction in allPredictions:
            if prediction in visited:
                continue
            similar = []
            for p in allPredictions:
                if comparisonFunction(prediction, p):
                    similar.append(p)
                    visited.append(p)
            groupped.append(similar)
        return groupped

    allPredictions = [] 
    [ allPredictions.extend(el) for el in allStationPredictions]

    groupped = groupSimilarPasses(allPredictions)

    merged = []
    for group in groupped:
        if len(group) < len(allStationPredictions):
            continue
        newStart = min([e.start for e in group])
        newEnd = max([e.end for e in group])
        newElev = max([e.maxElev for e in group])
        newAosAzimuth = [e.aosAzimuth for e in group if e.start == newStart][0]
        newPrediction = Predicton(newStart, newEnd, newElev, newAosAzimuth)
        print newPrediction
        merged.append(newPrediction)

    return merged


def generateSessions(predictions, minElev):
    sessions = []
    for sat_pass in predictions:
        if sat_pass.maxElev >= minElev:
            session = OrderedDict()
            session['short_description'] = "Automatic session."
            session['phase'] = "after_sail_deployment"
            session['status'] = "auto"
            session['primary'] = "elka" if (sat_pass.aosAzimuth < 90.0 or sat_pass.aosAzimuth > 270.0) else "fp"
            session['start_time_iso_with_zone'] = sat_pass.getIsoStartDate()
            session['stop_time_iso_with_zone'] = sat_pass.getIsoEndDate()
            session['maximum_elevation'] = sat_pass.maxElev

            sessionObject = dict()
            sessionObject['Session']=session

            sessions.append(sessionObject)
    return sessions

def saveSessions(sessionNumber, sessionsData, missionPath):
    sessionIndex = sessionNumber
    for session in sessionsData:
        sessionFolderPath = os.path.join(missionPath, "sessions", str(sessionIndex))
        os.mkdir(sessionFolderPath)
        dataPath = os.path.join(sessionFolderPath,"data.json")
        print dataPath
        with open(dataPath, "w") as outFile:
            json.dump(session, outFile, indent=4)
        sessionIndex = sessionIndex + 1

def qthListToQth(qthlist):
    qths = []
    for place in qthlist:
        qths.append((place[0], -place[1], place[2]))
    return qths


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', required=False,
                        help="Config file (in CMake-generated integration tests format)",
                        default=os.path.join(os.path.dirname(__file__), '../../config.py'))
    parser.add_argument('-s', '--session', required=False,
                        help="Next session number", type=int)
    parser.add_argument('-n', '--session-count', required=False,
                        help="Number of sessions to generate", default=1, type=int)
    parser.add_argument('-m', '--mission-path', required=False,
                        help="Path to Mission repository", default="~/gs/mission")
    
    args = parser.parse_args()
    imp.load_source('config', args.config)
    from config import config

    if "QTH" not in config:
        print "Ground Station location not found in config file. Exiting."
        return -1

    gpredict_path = "~/.config/GPredict/satdata/" if 'GPREDICT_PATH' not in config else config['GPREDICT_PATH']
    noradId = 43814 if 'NORAD_ID' not in config else config['NORAD_ID']
    minimum_elevation = 1 if 'MINIMUM_ELEVATION' not in config else config['MINIMUM_ELEVATION']

    qths = qthListToQth(config['QTH'])

    tleLoadter = GpredictTleLoader(gpredict_path)
    tleLines = tleLoadter.loadTle(noradId)
    allStationPredictions = predict_pass("\n".join(tleLines), qths, args.session_count)
    mergedPredictions = mergeStationPredictions(allStationPredictions)
    sessions = generateSessions(mergedPredictions, minimum_elevation)

    if args.session:
        saveSessions(args.session, sessions, args.mission_path)
    else:
        for s in sessions:
            print json.dumps(s, indent=4)

if __name__ == "__main__":
    main()