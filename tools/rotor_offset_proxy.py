import socket
import time
import parse
import argparse
import sys, os
import imp
import multiprocessing
import logging


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', required=True,
                        help="Config with azimuth and elevation offsets",
                        default=os.path.join(os.path.dirname(__file__), '../../config.py'))


    args = parser.parse_args()
    imp.load_source('config', args.config)
    from config import config

    if not config.viewkeys() >= {'AZ_OFFSET', 'EL_OFFSET', 'GPREDICT_PORT', 'ROTCTRLD_PORT'}:
        print("Both azimuth and elevation offsets must be specified in config file. Exiting.")
        return -1
    else:
        print("Config OK!")
        print("AZ_OFFSET: {} deg".format(config['AZ_OFFSET']))
        print("EL_OFFSET: {} deg".format(config['EL_OFFSET']))
        print("GPREDICT_PORT: {} deg".format(config['GPREDICT_PORT']))
        print("ROTCTRLD_PORT: {} deg".format(config['ROTCTRLD_PORT']))

    return config


def main():
    logger = logging.getLogger()
    logger.info('Starting...')
    config = parse_args()

    while True:
        rotctrld_socket = connect_rotctrld(config)
        gpredict_socket = connect_gpredict(config)

        thread_gpredict_to_rotctrld = multiprocessing.Process(target=gpredict_to_rotctrld, args=(config, rotctrld_socket, gpredict_socket, ))
        thread_rotctrld_to_gpredict = multiprocessing.Process(target=rotctrld_to_gpredict, args=(config, rotctrld_socket, gpredict_socket, ))

        thread_gpredict_to_rotctrld.start()
        thread_rotctrld_to_gpredict.start()


        while thread_gpredict_to_rotctrld.is_alive() and thread_rotctrld_to_gpredict.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info('Ending...')
                thread_gpredict_to_rotctrld.terminate()
                thread_rotctrld_to_gpredict.terminate()
                exit(0)


        gpredict_socket.close()
        rotctrld_socket.close()

        try:
            thread_gpredict_to_rotctrld.termiante()
        except:
            pass

        try:
            thread_rotctrld_to_gpredict.terminate()
        except:
            pass


def gpredict_to_rotctrld(config, rotctrld_socket, gpredict_socket):
    try:
        while True:
            data = gpredict_socket.recv(1024)
            if not data:
                break

            if data.startswith('P'):
                parsed = parse.parse("P {} {}", data)

                az = int(parsed[0].split(",")[0]) + config['AZ_OFFSET']

                if az < 0:
                    az = az + 360

                el = int(parsed[1].split(",")[0]) + config['EL_OFFSET']

                output_message = "P {} {}\n".format(az, el)
                rotctrld_socket.send(output_message)
                print("-> {}".format(output_message))
            else:
                rotctrld_socket.send(data)
                print("-> {}".format(data))

        print("gpredict_to_rotctrld disconneted!")
        gpredict_socket.close()
        rotctrld_socket.close()

    except:
        print("gpredict_to_rotctrld exception!")
        gpredict_socket.close()
        rotctrld_socket.close()



def rotctrld_to_gpredict(config, rotctrld_socket, gpredict_socket):
    try:
        while True:
            data = rotctrld_socket.recv(1024)
            if not data:
                break

            print("<- {}".format(data))
            parsed = parse.parse("{:.6f}\n{:.6f}", data)
            if parsed is not None:
                az = parsed[0] - config['AZ_OFFSET']
                el = parsed[1] - config['EL_OFFSET']
                message = "{:.6f}\n{:.6f}\n".format(az, el)
                print("to GPredict > {:.6f} {:.6f}".format(az, el))
                gpredict_socket.send(message)
            else:
                gpredict_socket.send(data)

        print("rotctrld_to_gpredict disconneted!")
        gpredict_socket.close()
        rotctrld_socket.close()

    except:
        print("rotctrld_to_gpredict exception!")
        gpredict_socket.close()
        rotctrld_socket.close()



def connect_rotctrld(config):
    rotctrld_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            rotctrld_socket.connect(('localhost', config['ROTCTRLD_PORT']))
            break
        except rotctrld_socket.error:
            print("Wait for rotctrld")
            time.sleep(1)

    print("rotctrld Connected!")
    time.sleep(2)

    return rotctrld_socket


def connect_gpredict(config):
    bind_to = ('localhost', config['GPREDICT_PORT'])
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(bind_to)
    server.listen(0)

    print("Waiting for connection on: %s:%d" % bind_to)
    sock, addr = server.accept()

    print("Connected from: %s:%d" % (addr[0], addr[1]))

    return sock

if __name__ == '__main__':
    main()