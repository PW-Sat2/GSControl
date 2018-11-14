tasks = [
    [tc.SetBitrate(3, 3), SendReceive, WaitMode.NoWait],
    [tc.SetBitrate(1, 8), SendReceive, WaitMode.NoWait],
    [tc.SendBeacon(), SendReceive, WaitMode.NoWait],
    [tc.SendBeacon(), Send, WaitMode.NoWait],
    [tc.ListFiles(1, '/'), Send, WaitMode.NoWait],
    [tc.ResetTransmitterTelecommand(), Send, WaitMode.NoWait],
    [tc.DownloadFile(17, '/telemetry.current', [i for i in range(0, 240, 7)]), Send, WaitMode.Wait],
    [tc.DownloadFile(18, '/telemetry.current', [i for i in range(240, 480, 7)]), Send, WaitMode.Wait],
    [tc.DownloadFile(19, '/telemetry.current', [i for i in range(480, 720, 7)]), Send, WaitMode.Wait],
    [tc.DownloadFile(20, '/telemetry.current', [i for i in range(720, 960, 7)]), Send, WaitMode.Wait],
    [tc.SendBeacon(), Send, WaitMode.NoWait],
    [tc.SendBeacon(), Send, WaitMode.NoWait],
    [tc.SetBitrate(1, 1), SendReceive, WaitMode.NoWait],
    [tc.SendBeacon(), Send, WaitMode.NoWait]
]
