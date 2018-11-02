tasks = [
    [tc.SetBuiltinDetumblingBlockMaskTelecommand(1, 2), SendReceive, WaitMode.NoWait],
    [tc.SetBuiltinDetumblingBlockMaskTelecommand(1, 2), SendReceive, WaitMode.NoWait],
    [tc.WriteProgramPart([0, 1, 2], 0, [i for i in range(0, 196, 1)]), SendReceive, WaitMode.NoWait]
]
