from auto_session.conditions import Received, Or, Iterations, PointOfTime, Eternity
from auto_session.session_base import Loop
from devices import BaudRate
from radio.task_actions import Send, Sleep
import telecommand as tc
import response_frames as rf


def session(start, stop):
    yield Loop(
        title="Ensure bitrate 9600",
        tasks=[
            [10, Sleep],
            [tc.SetBitrate(correlation_id=12, bitrate=BaudRate.BaudRate9600), Send],
        ],
        until=Received(rf.SetBitrateSuccessFrame)
    )

    yield Loop(
        title="Get few beacons",
        tasks=[
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ],
        until=Received(rf.BeaconFrame, min_count=2)
    )

    yield Loop(
        title="Get file list",
        tasks=[
            [tc.ListFiles(correlation_id=13, path='/'), Send],
            [10, Sleep],
            [tc.SendBeacon(), Send],
            [10, Sleep]
        ],
        until=Received(rf.FileListSuccessFrame)
    )

    yield Loop(
        title="Get beacons at the end",
        tasks=[
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ],
        until=Eternity
    )