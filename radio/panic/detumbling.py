tasks = [
    [tc.SetAdcsModeTelecommand(11, AdcsMode.Stopped), Send, WaitMode.NoWait],
    [3, Sleep, WaitMode.NoWait],
    [tc.SetAdcsModeTelecommand(12, AdcsMode.Stopped), Send, WaitMode.NoWait],
    [3, Sleep, WaitMode.NoWait],
    [tc.SetAdcsModeTelecommand(13, AdcsMode.Stopped), Send, WaitMode.NoWait],
    [3, Sleep, WaitMode.NoWait],

    [tc.SetAdcsModeTelecommand(14, AdcsMode.BuiltinDetumbling), Send, WaitMode.NoWait],
    [3, Sleep, WaitMode.NoWait],
    [tc.SetAdcsModeTelecommand(15, AdcsMode.BuiltinDetumbling), Send, WaitMode.NoWait],
    [3, Sleep, WaitMode.NoWait],
    [tc.SetAdcsModeTelecommand(16, AdcsMode.BuiltinDetumbling), Send, WaitMode.NoWait],
    [3, Sleep, WaitMode.NoWait],
    [[tc.SendBeacon(), 15], SendLoop, WaitMode.NoWait],
]
