tasks = [
    [tc.PingTelecommand(), SendLoop(10), WaitMode.NoWait],
    [tc.SendBeacon(), SendLoop(10), WaitMode.NoWait],
    [tc.ListFiles(1, '/'), SendLoop(5), WaitMode.NoWait],
    [tc.SendBeacon(), SendLoop(10), WaitMode.NoWait]
]
