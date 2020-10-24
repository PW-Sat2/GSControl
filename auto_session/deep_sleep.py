from auto_session.conditions import Received, Or, Iterations, PointOfTime, Eternity
from auto_session.session_base import Loop
from devices import BaudRate
from radio.task_actions import Send, Sleep
import telecommand as tc
import response_frames as rf


def session(start, stop):
    yield Loop(
        title="Get few beacons",
        tasks=[
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ],
        until=Received(rf.little_oryx.LittleOryxDeepSleepBeacon, min_count=2)
    )

    yield Loop(
        title="Delay reboot",
        tasks=[
            [tc.little_oryx.DelayRebootToNormal(10, 48), Send], # 3.5 days
            [20, Sleep],
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ],
        until=Received(rf.little_oryx.DelayRebootSuccessFrame)
    )

    yield Loop(
        title="Get beacons at the end",
        tasks=[
            [tc.SendBeacon(), Send],
            [20, Sleep]
        ],
        until=Eternity()
    )
