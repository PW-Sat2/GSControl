tasks = [[tc.SendBeacon(), SendReceive, 'NoWait'],
[tc.SendBeacon(), SendReceive, 'NoWait'],
[tc.CopyBootSlots(4, 0x38, 0x07), SendReceive, 'NoWait'],
[tc.SendBeacon(), SendReceive, 'NoWait'],
[tc.SendBeacon(), SendReceive, 'NoWait'],
]
