tasks = [[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
[tc.EnterIdleState(3, 144), Send, WaitMode.NoWait],
[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
]
