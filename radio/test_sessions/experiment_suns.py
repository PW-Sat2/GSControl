tasks = [[tc.SetBitrate(50, 8), Send, WaitMode.Wait],
[tc.SetBitrate(51, 8), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.NoWait],
[tc.ListFiles(52, '/'), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.DownloadFile(57, '/rad', [24, 25, 26, 27, 28]), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.NoWait],
[tc.SendBeacon(), Send, WaitMode.NoWait],
[tc.DownloadFile(59, '/telemetry.current', [i for i in range(1300, 1325, 2)]), Send, WaitMode.Wait],
[tc.DownloadFile(60, '/telemetry.current', [i for i in range(1325, 1350, 2)]), Send, WaitMode.Wait],
[tc.DownloadFile(61, '/telemetry.current', [i for i in range(1350, 1375, 2)]), Send, WaitMode.Wait],
[tc.DownloadFile(62, '/telemetry.current', [i for i in range(1375, 1400, 2)]), Send, WaitMode.Wait],
[tc.DownloadFile(62, '/telemetry.current', [i for i in range(1400, 1425, 2)]), Send, WaitMode.Wait],
[tc.DownloadFile(64, '/telemetry.current', [i for i in range(1425, 1450, 2)]), Send, WaitMode.Wait],
[tc.DownloadFile(65, '/telemetry.current', [i for i in range(1450, 1475, 2)]), Send, WaitMode.NoWait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.PerformSunSExperiment(66, 0, 10, 10, datetime.timedelta(seconds=1), 10, datetime.timedelta(minutes=3), 'suns'), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.NoWait],
[tc.SendBeacon(), Send, WaitMode.NoWait],
]