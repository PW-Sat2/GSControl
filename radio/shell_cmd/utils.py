def build(sender, rcv, frame_decoder, *args):
    def send_and_parse_beacon():
        from tools.parse_beacon import ParseBeacon
        from telecommand import SendBeacon

        sender.send(SendBeacon())
        data = rcv.decode_kiss(rcv.receive())
        beacon = frame_decoder.decode(data)

        return ParseBeacon.parse(beacon)

    return {
        'send_and_parse_beacon': send_and_parse_beacon
    }