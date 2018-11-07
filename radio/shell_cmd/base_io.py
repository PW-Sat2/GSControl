def build(sender, rcv, frame_decoder, *args):
    def receive():
        """
        Receives and decodes single frame. 
        Blocks until frame is received
        """
        data = rcv.decode_kiss(rcv.receive())
        return frame_decoder.decode(data)

    def receive_raw():
        """
        Receives single frame. 
        Blocks until frame is received
        """
        return rcv.decode_kiss(rcv.receive())

    def set_timeout(timeout_in_ms=-1):
        """
        Changes receiver timeout (in ms).
        -1 for infintity
        """
        rcv.timeout(timeout_in_ms)

    def send(frame):
        """Sends single frame"""
        sender.send(frame)

    def send_receive(frame):
        """Sends single frame and immediately receives one (probably a response to just sent frame)"""
        send(frame)
        return receive()

    def get_sender():
        return sender

    def get_receiver():
        return rcv

    def receiver_loop():
        """
        Receives all incoming frames and decodes them.
        Use Ctrl+C to break the loop.
        Captured frames are returned from this function
        """
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