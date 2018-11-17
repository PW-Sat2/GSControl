tasks = [
    [[tc.SendBeacon(), 3], SendLoop, WaitMode.NoWait],
    [tc.SendBeacon(), SendReceive, WaitMode.NoWait],
    ["It just prints a message.", Print, WaitMode.NoWait],
    [tc.ListFiles(1, '/'), Send, WaitMode.NoWait],
    ["The next action sleeps for 5s.", Print, WaitMode.NoWait],
    [5, Sleep, WaitMode.NoWait],
    [tc.DownloadFile(17, '/telemetry.current', [i for i in range(0, 240, 7)]), Send, WaitMode.Wait],
    [tc.SendBeacon(), Send, WaitMode.NoWait],
    [tc.SendBeacon(), Send, WaitMode.NoWait]
]
