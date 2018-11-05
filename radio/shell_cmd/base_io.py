def build(sender, rcv, frame_decoder, *args):
    def receive():
        data = rcv.decode_kiss(rcv.receive())
        return frame_decoder.decode(data)

    def receive_raw():
        return rcv.decode_kiss(rcv.receive())

    def set_timeout(timeout_in_ms=-1):
        rcv.timeout(timeout_in_ms)

    def send(frame):
        sender.send(frame)

    def send_receive(frame):
        send(frame)
        return receive()

    def get_sender():
        return sender

    def get_receiver():
        return rcv

    def receiver_loop():
        import pprint
        frames = []
        
        try:
            while True:
                x = receive()
                pprint.pprint(x)
                frames.append(x)
        except KeyboardInterrupt:
            pass
        finally:
            return frames

    return {
        'receive_raw': receive_raw, 
        'receive': receive,
        'send_receive': send_receive,
        'set_timeout': set_timeout, 
        'send': send,
        'receiver_loop': receiver_loop
    }