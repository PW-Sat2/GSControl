tasks = [[tc.SetBitrate(50, 8), Send, WaitMode.Wait],
[tc.SetBitrate(51, 8), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.ListFiles(52, '/'), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.DownloadFile(57, '/rad', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.TakePhotoTelecommand(58, camera.CameraLocation.Nadir, camera.PhotoResolution.p480, 1, datetime.timedelta(minutes=2), 'p0'), Send, WaitMode.NoWait],
[tc.TakePhotoTelecommand(58, camera.CameraLocation.Nadir, camera.PhotoResolution.p480, 2, datetime.timedelta(minutes=1), 'p1'), Send, WaitMode.NoWait],
[tc.TakePhotoTelecommand(58, camera.CameraLocation.Nadir, camera.PhotoResolution.p480, 4, datetime.timedelta(minutes=1), 'p2'), Send, WaitMode.NoWait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.DownloadFile(59, '/telemetry.current', [i for i in range(1105, 1135, 2)]), Send, WaitMode.NoWait],
[tc.DownloadFile(60, '/telemetry.current', [i for i in range(1135, 1165, 2)]), Send, WaitMode.NoWait],
[tc.DownloadFile(61, '/telemetry.current', [i for i in range(1165, 1195, 2)]), Send, WaitMode.NoWait],
[tc.DownloadFile(62, '/telemetry.current', [i for i in range(1195, 1225, 2)]), Send, WaitMode.NoWait],
[tc.DownloadFile(63, '/telemetry.current', [i for i in range(1225, 1255, 2)]), Send, WaitMode.NoWait],
[tc.DownloadFile(64, '/telemetry.current', [i for i in range(1255, 1285, 2)]), Send, WaitMode.NoWait],
[tc.DownloadFile(65, '/telemetry.current', [i for i in range(1285, 1315, 2)]), Send, WaitMode.NoWait],
[tc.SendBeacon(), Send, WaitMode.Wait],
[tc.SendBeacon(), Send, WaitMode.Wait],
]
