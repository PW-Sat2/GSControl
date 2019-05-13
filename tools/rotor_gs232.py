import socket
import time
import serial

import parse

rot = serial.Serial('/dev/rotor', 600)

bind_to = ('', 4533)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(bind_to)
server.listen(0)

time.sleep(0.5)  # TODO: Find better way to know if init is all done

while True:
    print "Waiting for connection on: %s:%d" % bind_to
    sock, addr = server.accept()

    print "Connected from: %s:%d" % (addr[0], addr[1])

    while True:
        data = sock.recv(1024)
        print(data)
        if not data:
            break

        if data.startswith('P'):
            parsed = parse.parse("P {} {}", data)

            az = int(parsed[0].split(",")[0])
            el = int(parsed[1].split(",")[0])

            rot.write("W{:03d} {:03d}\n".format(az, el))

            sock.sendall("RPRT 0\n")
        elif data.startswith('p'):
            sock.sendall("p\n0\n0")

    sock.close()
    rot.close()
    print "Disconnected from: %s:%d" % (addr[0], addr[1])
