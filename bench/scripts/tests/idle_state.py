from bench_init import *


def run():
    check(tm.COMM.TX.IdleState, False, 0)

    send(tc.comm.EnterIdleState(100))
    check(tm.COMM.TX.IdleState, True, 0)
    check(tm.COMM.TX.IdleState, False, 100)

    send(tc.comm.EnterIdleState(255))
    check(tm.COMM.TX.IdleState, True, 0)
    send(tc.comm.EnterIdleState(0))
    check(tm.COMM.TX.IdleState, False, 0)
