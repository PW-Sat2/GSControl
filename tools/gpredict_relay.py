import socket
import time
import multiprocessing

frequency = multiprocessing.Value('i', 0)


def set_freq(freq):
    with frequency.get_lock():
        frequency.value = freq


def gpredict():
    bind_to = ('', 4400)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(bind_to)
    server.listen(0)

    time.sleep(0.5)  # TODO: Find better way to know if init is all done

    while True:
        print "Waiting for connection on: %s:%d" % bind_to
        sock, addr = server.accept()

        print "Connected from: %s:%d" % (addr[0], addr[1])

        cur_freq = 0
        while True:
            data = sock.recv(1024)
            if not data:
                break

            if data.startswith('F'):
                freq = int(data[1:].strip())
                if cur_freq != freq:
                    print "New frequency: %d" % freq

                    set_freq(freq)

                    cur_freq = freq
                sock.sendall("RPRT 0\n")
            elif data.startswith('f'):
                sock.sendall("f: %d\n" % cur_freq)

        sock.close()
        print "Disconnected from: %s:%d" % (addr[0], addr[1])



def gnuradio():
    gnuradio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            gnuradio_socket.connect(('localhost', 4532))
            break
        except socket.error:
            print "Wait for gnuradio"
            time.sleep(1)

    gnuradio_socket.settimeout(0.1)
    print "Gnuradio Connected!"

    while 1:
        try:
            data = gnuradio_socket.recv(1024)
            if not data:
                # disconnected
                break
            # print ">", data
        except socket.timeout:
            # print "A"
            frequency_now = None

            with frequency.get_lock():
                if frequency.value != 0:
                    frequency_now = frequency.value
                    frequency.value = 0

            if frequency_now:
                gnuradio_socket.send('F' + str(frequency_now) + '\n')
        except Exception as e:
            print e
            break

    print "Gnuradio disconnected!"
    gnuradio_socket.shutdown(socket.SHUT_RDWR)
    gnuradio_socket.close()


t = multiprocessing.Process(target=gpredict)
t2 = multiprocessing.Process(target=gnuradio)

while True:
    try:
        if not t.is_alive():
            t = multiprocessing.Process(target=gpredict)
            t.start()
        if not t2.is_alive():
            t2 = multiprocessing.Process(target=gnuradio)
            t2.start()
        time.sleep(1)

    except KeyboardInterrupt:
        print "Ending!"
        t.terminate()
        t2.terminate()
        exit(0)


