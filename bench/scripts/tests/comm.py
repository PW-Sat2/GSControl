from bench_init import *


@make_test
def test_comm_idle_state():
    tm.assert_false(tm.COMM.TX.IdleState)

    send(tc.comm.EnterIdleState(100))
    tm.assert_true(tm.COMM.TX.IdleState)
    tm.assert_false(tm.COMM.TX.IdleState, timeout=100)

    send(tc.comm.EnterIdleState(255))
    tm.assert_true(tm.COMM.TX.IdleState)

    send(tc.comm.EnterIdleState(0))
    tm.assert_false(tm.COMM.TX.IdleState)
