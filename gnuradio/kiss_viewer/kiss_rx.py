import kiss


def print_frame(frame):
    #print(frame)
    print len(frame)-17, ":: ",
    for i in frame[17:]:
    #for i in frame:
        print hex(ord(i)),
    print "\n\n"


def main():
    ki = kiss.TCPKISS(host='localhost', port=52001)
    ki.start()
    ki.read(callback=print_frame)


if __name__ == '__main__':
    main()
