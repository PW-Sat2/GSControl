tasks = [
    [tc.SetBitrate(1, 8), SendReceive, "NoWait"],
    [tc.SendBeacon(), SendReceive, "NoWait"],
    [tc.SendBeacon(), "Send", "NoWait"],
    [tc.ListFiles(1, '/'), "Send", "NoWait"],
    [tc.ResetTransmitterTelecommand(), "Send", "NoWait"],
    [tc.DownloadFile(17, '/telemetry.current', [i for i in range(0, 240, 7)]), "Send", "Wait"],
    [tc.DownloadFile(18, '/telemetry.current', [i for i in range(240, 480, 7)]), "Send", "Wait"],
    [tc.DownloadFile(19, '/telemetry.current', [i for i in range(480, 720, 7)]), "Send", "Wait"],
    [tc.DownloadFile(20, '/telemetry.current', [i for i in range(720, 960, 7)]), "Send", "Wait"],
    [tc.SendBeacon(), "Send", "NoWait"],
    [tc.SendBeacon(), "Send", "NoWait"],
    [tc.SetBitrate(1, 1), SendReceive, "Nowait"],
    [tc.SendBeacon(), "Send", "NoWait"]
]
