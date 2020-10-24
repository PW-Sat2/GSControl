from auto_session.conditions import Received, Or, Iterations, PointOfTime, Eternity
from auto_session.session_base import Loop
from devices import BaudRate
from radio.task_actions import Send, Sleep
import telecommand as tc
import response_frames as rf


def session(start, stop):
    yield Loop(
        title="Get beacons at the end",
        tasks=[
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ],
        until=Eternity()
    )
