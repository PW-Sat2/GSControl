tasks = [
    [tc.SendBeacon(), SendReceive, WaitMode.NoWait],
    [tc.SendBeacon(), Print("It shows how the Print() action works. It does not send any telecommand. It just prints a message."), WaitMode.NoWait],
    [tc.ListFiles(1, '/'), Send, WaitMode.NoWait],
    [tc.SendBeacon(), Print("Print a message, again. But the next action sleeps for 5s. It also does not send any telecommand."), WaitMode.NoWait],
    [tc.SendBeacon(), Sleep(5), WaitMode.NoWait],
    [tc.DownloadFile(17, '/telemetry.current', [i for i in range(0, 240, 7)]), Send, WaitMode.Wait],
    [tc.SendBeacon(), Send, WaitMode.NoWait],
    [tc.SendBeacon(), Send, WaitMode.NoWait]
]
