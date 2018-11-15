from enum import Enum, unique

class SendReceive(object):
    def __init__(self, arg):
        self.telecommand = arg

    def do(self, comm):
        comm.send_receive(self.telecommand)


class Send(object):
    def __init__(self, arg):
        self.telecommand = arg

    def do(self, comm):
        comm.send(self.telecommand)


class SendLoop(object):
    ITERATION_INDICATOR = "#"
    SLEEP_STEP = 0.1

    def __init__(self, iteration_seconds):
        self.iteration_seconds = iteration_seconds
        self.__name__ = "SendLoop"

    def do(self, comm, telecommand):
        from prompt_toolkit.shortcuts import print_tokens
        from prompt_toolkit.styles import style_from_dict
        from pygments.token import Token
        from time import sleep

        print " <Ctrl+C> to break SendLoop({}s).".format(str(self.iteration_seconds))
        try:
            while True:
                comm.send(telecommand)

                print_tokens([
                    (Token.Msg, self.ITERATION_INDICATOR),
                ], style=style_from_dict({Token.Msg: 'reverse'}))
                
                sleep_step = 0
                while sleep_step < self.iteration_seconds:
                    sleep_step += self.SLEEP_STEP
                    sleep(self.SLEEP_STEP)

        except KeyboardInterrupt:
            pass


class Print(object):
    def __init__(self, text):
        self.text = text
        self.__name__ = "Print"

    def do(self, comm):
        from prompt_toolkit.shortcuts import print_tokens
        from prompt_toolkit.styles import style_from_dict
        from pygments.token import Token

        print_tokens([
            (Token, "\n"),
            (Token.Msg, self.text),
            (Token, "\n"),
        ], style=style_from_dict({Token.Msg: 'reverse'}))


class Sleep(object):
    def __init__(self, arg):
        self.seconds = arg
        self.__name__ = "Sleep"

    def do(self, comm):
        from prompt_toolkit.shortcuts import print_tokens
        from prompt_toolkit.styles import style_from_dict
        from pygments.token import Token
        from time import sleep

        print_tokens([
            (Token, "\n"),
            (Token.Msg, "Sleep for {}s...".format(str(self.seconds))),
            (Token, "\n"),
        ], style=style_from_dict({Token.Msg: 'reverse'}))

        sleep(self.seconds)

@unique
class WaitMode(Enum):
    Wait = 1,
    NoWait = 2,
    def __str__(self):
        map = {
            self.Wait: "Wait",
            self.NoWait: "NoWait"
        }

        return map[self]
