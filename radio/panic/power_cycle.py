tasks = [
    [tc.PowerCycleTelecommand(1), Send, WaitMode.NoWait],
    [2, Sleep, WaitMode.NoWait],
    [tc.PowerCycleTelecommand(2), Send, WaitMode.NoWait],
    [2, Sleep, WaitMode.NoWait],
    [tc.PowerCycleTelecommand(3), Send, WaitMode.NoWait],
    [2, Sleep, WaitMode.NoWait],
    [tc.RawI2C(13, 0, 0x35, 1, [0xE0]), Send, WaitMode.NoWait], # EPS A power cycle
    [2, Sleep, WaitMode.NoWait],
    [tc.RawI2C(13, 0, 0x35, 1, [0xE0]), Send, WaitMode.NoWait], # EPS A power cycle
    [2, Sleep, WaitMode.NoWait],
    [tc.RawI2C(13, 0, 0x35, 1, [0xE0]), Send, WaitMode.NoWait], # EPS A power cycle
    [2, Sleep, WaitMode.NoWait],
    [tc.PowerCycleTelecommand(7), Send, WaitMode.NoWait],
    [2, Sleep, WaitMode.NoWait],
    [tc.RawI2C(13, 0, 0x35, 1, [0xE0]), Send, WaitMode.NoWait], # EPS A power cycle
    [2, Sleep, WaitMode.NoWait],
    [tc.PowerCycleTelecommand(9), Send, WaitMode.NoWait],
    [2, Sleep, WaitMode.NoWait],
    [tc.RawI2C(13, 0, 0x35, 1, [0xE0]), Send, WaitMode.NoWait], # EPS A power cycle
    [20, Sleep, WaitMode.NoWait],
    [[tc.SendBeacon(), 15], SendLoop, WaitMode.NoWait],
]
