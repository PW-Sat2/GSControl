tasks = [
    [tc.SetBuiltinDetumblingBlockMaskTelecommand(1, 2), SendReceive, WaitMode.NoWait],
    [tc.SetBuiltinDetumblingBlockMaskTelecommand(1, 2), SendReceive, WaitMode.NoWait],
    [tc.DownloadFile(2, 'a' * 101, [1]), SendReceive, WaitMode.NoWait],
    [tc.DownloadFile(2, 'file_path', [i for i in range(0, 39, 1)]), SendReceive, WaitMode.NoWait],
    [tc.WriteProgramPart([0, 1, 2], 0, [i for i in range(0, 196, 1)]), SendReceive, WaitMode.NoWait]
]
