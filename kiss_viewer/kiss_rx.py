import kiss


def print_frame(frame):
    # print(frame)
    for i in frame[:17]:
        print hex(ord(i)),
    print ""


def main():
    ki = kiss.TCPKISS(host='localhost', port=52001)
    ki.start()
    ki.read(callback=print_frame)


if __name__ == '__main__':
    main()
