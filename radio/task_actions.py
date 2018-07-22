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


class Print(object):
    def __init__(self, text):
        self.text = text

    def do(self, comm):
        from prompt_toolkit.shortcuts import print_tokens
        from prompt_toolkit.styles import style_from_dict
        from pygments.token import Token

        print_tokens([
            (Token, "\n\t"),
            (Token.Msg, self.text),
            (Token, "\n"),
        ], style=style_from_dict({Token.Msg: 'reverse'}))


class Sleep(object):
    def __init__(self, arg):
        self.seconds = arg

    def do(self, comm):
        from time import sleep
        sleep(self.seconds)


