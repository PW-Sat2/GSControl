import socket
import time
import multiprocessing
import logging
import argparse
import colorlog

frequency = multiprocessing.Value('i', 0)

def setup_log(silent):
    logging.Formatter.converter = time.gmtime
    root_logger_std = logging.getLogger()
    console_handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)-15s %(levelname)s: [%(name)s] %(message)s",
        log_colors={
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    console_handler.setFormatter(formatter)
    root_logger_std.addHandler(console_handler)

    if silent:
        root_logger_std.setLevel(logging.INFO)
    else:
        root_logger_std.setLevel(logging.DEBUG)


def set_freq(freq):
    with frequency.get_lock():
        frequency.value = freq


def gpredict():
    log = logging.getLogger("GPredict")
    bind_to = ('', 4400)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(bind_to)
    server.listen(0)

    time.sleep(0.5)  # TODO: Find better way to know if init is all done

    while True:
        log.debug("Waiting for connection on: %s:%d" % bind_to)
        try:
            sock, addr = server.accept()
        except KeyboardInterrupt:
            log.info("Keyboard interrupt. Exiting.")
            break

        log.info("Connected from: %s:%d" % (addr[0], addr[1]))

        cur_freq = 0
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    break

                if data.startswith('F'):
                    freq = int(data[1:].strip())
                    if cur_freq != freq:
                        log.debug("New frequency: %d" % freq)

                        set_freq(freq)

                        cur_freq = freq
                    sock.sendall("RPRT 0\n")
                elif data.startswith('f'):
                    sock.sendall("f: %d\n" % cur_freq)
            except KeyboardInterrupt:
                log.info("Keyboard interrupt. Exiting.")
                sock.close()
                break             

        sock.close()
        log.info("Disconnected from: %s:%d" % (addr[0], addr[1]))


def gnuradio():
    log = logging.getLogger("Gnuradio")
    gnuradio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_connected = False

    while True:
        try:
            gnuradio_socket.connect(('localhost', 4532))
            gnuradio_socket.settimeout(0.1)
            log.info("Gnuradio Connected!")
            is_connected = True
            break
        except socket.error:
            log.debug("Wait for gnuradio")
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
            
    time.sleep(2)

    while is_connected:
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
        except KeyboardInterrupt:
            log.info("Keyboard interrupt")
            break           
        except Exception as e:
            log.exception("Error in processing", exc_info=e)
            break

    log.info("Gnuradio disconnected!")
    gnuradio_socket.shutdown(socket.SHUT_RDWR)
    gnuradio_socket.close()


def main(args):
    t = multiprocessing.Process(target=gpredict)
    t2 = multiprocessing.Process(target=gnuradio)

    setup_log(args.silent)
    log = logging.getLogger("Main")

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
            log.info("Ending!")
            t.terminate()
            t2.terminate()
            exit(0)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--silent', action='store_true',
                        help="Suppress most of output (service use)")

    return parser.parse_args()

if __name__ == '__main__': 
    main(parse_args())