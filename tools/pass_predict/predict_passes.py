# -*- coding: utf-8 -*-

from gpredict_tle_loader import GpredictTleLoader
from prediction import Predicton
import predict
import argparse
import os
import imp
import datetime
import json
from collections import OrderedDict
import time

def predict_pass(tle, qths, end_datetime, count):
    def predictOneStation(tle, qth):
        predictions = []
        p = predict.transits(tle, qth)

        while len(predictions) < count:
            transit = p.next()
            start = transit.start
            stop = transit.end
            maxElev = round(transit.peak()['elevation'], 2)
            aosAzimuth = transit.at(transit.start)['azimuth']

            prediction = Predicton(start, stop, maxElev, aosAzimuth)

            if start > end_datetime:
                predictions.append(prediction)

        return predictions
   
    allStationPredictions = []
    for station in qths:
        allStationPredictions.append(predictOneStation(tle, station))       

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


def generateSessions(predictions, min_elev, session_start_index, lastPowerCycleController, powerCycleMinElevation, lastPowerCycleSessionData):
    def tasksDescriptions(task):
        switcher = {
            "power-cycle-A" : "Power cycle EPS A. ",
            "power-cycle-B" : "Power cycle EPS B. ",
            "telemetry"     : "Telemetry download. ",
            "keep-alive"    : "Keep-alive session. "
        }
        return switcher.get(task, "")

    def generateDescription(session_tasks):
        desc_string = ""
        for task in session_tasks:
            desc_string += tasksDescriptions(task)
        return desc_string

    power_cycle_days = set()
    sessions = []
    session_index = session_start_index
    lastPowerCycleController = lastPowerCycleController

    power_cycle_days.add(datetime.datetime.strptime(lastPowerCycleSessionData['Session']['start_time_iso_with_zone'].split("T")[0], "%Y-%m-%d").date())

    for sat_pass in predictions:
        if sat_pass.maxElev >= min_elev:
            session = OrderedDict()
            session['index'] = session_index
            session['phase'] = "after_sail_deployment"
            session['primary'] = "elka" if (sat_pass.aosAzimuth < 90.0 or sat_pass.aosAzimuth > 270.0) else "fp"
            session['start_time_iso_with_zone'] = sat_pass.getIsoStartDateString()
            session['stop_time_iso_with_zone'] = sat_pass.getIsoEndDateString()
            session['maximum_elevation'] = sat_pass.maxElev

            
            day = sat_pass.getIsoStartDate().date()
            session_tasks = []

            if (day not in power_cycle_days) and (not (sat_pass.aosAzimuth < 90.0 or sat_pass.aosAzimuth > 270.0)) and (sat_pass.maxElev >= powerCycleMinElevation):
                currentPowerCycleController = "power-cycle-B" if lastPowerCycleController == "power-cycle-A" else "power-cycle-A"

                session_tasks = [currentPowerCycleController, 'telemetry']
                session['status'] = "planned"   

                lastPowerCycleController = currentPowerCycleController
                power_cycle_days.add(day)
            else:
                session_tasks = ['keep-alive']
                session['status'] = "auto"

            session['session_tasks'] = session_tasks
            session['short_description'] = generateDescription(session_tasks)
            sessionObject = dict()
            sessionObject['Session']=session

            sessions.append(sessionObject)

            session_index += 1
    return sessions

def fallbackDesc(desc):
    return """{{% extends "/sessions/_layout/index.md" %}}

{{% block goal %}}
{0}
{{% endblock %}}
""".format(desc)

def saveSessions(sessionNumber, sessionsData, missionPath):
    sessionIndex = sessionNumber
    for session in sessionsData:
        sessionFolderPath = os.path.join(missionPath, "sessions", str(sessionIndex))
        os.mkdir(sessionFolderPath)
        dataPath = os.path.join(sessionFolderPath, "data.json")
        print dataPath
        with open(dataPath, "w") as outFile:
            json.dump(session, outFile, indent=4)

        descPath = os.path.join(sessionFolderPath, "index.md")
        with open(descPath, "w") as outFile:
            outFile.write(fallbackDesc(session["Session"]["short_description"]))
        sessionIndex = sessionIndex + 1

def qthListToQth(qthlist):
    qths = []
    for place in qthlist:
        qths.append((place[0], -place[1], place[2]))
    return qths

def getSessionFolders(missionRepoPath):
    dirList = [name for name in os.listdir(os.path.join(missionRepoPath, 'sessions')) if os.path.isdir(os.path.join(missionRepoPath, 'sessions', name))]

    sessionDirs = []
    for d in dirList:
        try:
            sessionDirs.append(int(d))
        except:
            print("Not a session dir!")

    return sessionDirs

def getLastSessionData(missionRepoPath):
    sessionDirs = getSessionFolders(missionRepoPath)

    lastSessionDir = max(sessionDirs)
    with open(os.path.join(missionRepoPath, 'sessions', str(lastSessionDir), 'data.json'), 'r') as f:
        data = json.loads(f.read())

    data['index'] = lastSessionDir
    return data

def getLastSessionPowerCycleSession(missionRepoPath):
    sessionDirs = getSessionFolders(missionRepoPath)

    sessionDirsFromLast = sorted(sessionDirs, reverse=True)

    for sessionDir in sessionDirsFromLast:
        with open(os.path.join(missionRepoPath, 'sessions', str(sessionDir), 'data.json'), 'r') as f:
            data = json.loads(f.read())
            return data
    return None

def getLastPowerCycleController(data):
    try:
        data['Session']['session_tasks'].index("power-cycle-A")
        return "power-cycle-A"
    except:
        pass
    try:
        data['Session']['session_tasks'].index("power-cycle-B")
        return "power-cycle-B"
    except:
        pass

    return None

def fromLocalStringToTimestamp(timestampString):
    return (datetime.datetime.strptime(timestampString.split("+")[0], "%Y-%m-%dT%H:%M:%S") - datetime.datetime(1970, 1, 1)).total_seconds()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', required=False,
                        help="Config file (in CMake-generated integration tests format)",
                        default=os.path.join(os.path.dirname(__file__), '../../config.py'))
    parser.add_argument('-s', '--session', required=False,
                        help="Next session number", type=int)
    parser.add_argument('-n', '--session-count', required=False,
                        help="Number of sessions to generate", default=1, type=int)
    parser.add_argument('-p', '--power-cycle-min-elevation', required=False,
                        help="Minimum elevation for power cycle", default=20, type=int)
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

    lastSessionData = getLastSessionData(args.mission_path)
    
    lastPowerCycleSessionData = getLastSessionPowerCycleSession(args.mission_path)
    lastPowerCycleController = getLastPowerCycleController(lastPowerCycleSessionData)
    stop_time = fromLocalStringToTimestamp(lastSessionData['Session']['stop_time_iso_with_zone'])
    print("Last session stop time: {}".format(stop_time))

    qths = qthListToQth(config['QTH'])

    tleLoadter = GpredictTleLoader(gpredict_path)
    tleLines = tleLoadter.loadTle(noradId)
    allStationPredictions = predict_pass("\n".join(tleLines),
                                         qths,
                                         stop_time,
                                         args.session_count)

    mergedPredictions = mergeStationPredictions(allStationPredictions)

    nextSessionIndex = lastSessionData['index'] + 1
    sessions = generateSessions(mergedPredictions,
                                minimum_elevation,
                                nextSessionIndex,
                                lastPowerCycleController,
                                args.power_cycle_min_elevation,
                                lastPowerCycleSessionData)

    if args.session:
        saveSessions(args.session, sessions, args.mission_path)
    else:
        saveSessions(nextSessionIndex, sessions, args.mission_path)
        for s in sessions:
            print json.dumps(s, indent=4)

if __name__ == "__main__":
    main()