tasks = [
    [tc.SetBitrate(3, 3), SendReceive, WaitMode.NoWait],
    [tc.SetBitrate(1, 8), SendReceive, WaitMode.NoWait],
    [tc.SendBeacon(), SendReceive, WaitMode.NoWait],
    [tc.SendBeacon(), Send, WaitMode.NoWait],
    [tc.ListFiles(1, '/'), Send, WaitMode.NoWait],
    [tc.SetBitrate(1, 1), SendReceive, WaitMode.NoWait],
    [tc.PerformSailExperiment(6), "Send", "Wait"],
    [tc.SendBeacon(), Send, WaitMode.NoWait]
]
