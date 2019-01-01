from auto_session.conditions import Received, Or, Iterations
from auto_session.session_base import Loop
from devices import BaudRate
from radio.task_actions import Send, Sleep
import telecommand as tc
import response_frames as rf


def session():
    yield Loop(
        tasks=[
            [tc.SetBitrate(correlation_id=12, bitrate=BaudRate.BaudRate9600), Send],
            [5, Sleep]
        ],
        until=Received(rf.SetBitrateSuccessFrame)
    )

    yield Loop(
        tasks=[
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ],
        until=Received(rf.BeaconFrame, min_count=3)
    )

    yield Loop(
        tasks=[
            [tc.ListFiles(correlation_id=13, path='/'), Send],
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ],
        until=Or(
            Received(rf.FileListSuccessFrame),
            Iterations(5)
        )
    )

    yield Loop(
        tasks=[
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ]
    )