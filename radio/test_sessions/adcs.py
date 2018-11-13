tasks = [[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
[tc.SetAdcsModeTelecommand(10, -1), SendReceive, WaitMode.NoWait],
[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
[tc.SetAdcsModeTelecommand(11, 0), SendReceive, WaitMode.NoWait],
[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
[tc.SendBeacon(), SendReceive, WaitMode.NoWait],
]
