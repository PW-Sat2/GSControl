import pprint
from datetime import datetime

from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.styles import style_from_dict
from pygments.token import Token

STYLE = style_from_dict({
    Token.Timestamp: '#fdf6e3',
    Token.CurrentStep: '#b58900',
    Token.TotalSteps: '#6c71c4',
    Token.Action: '#dc322f',
    Token.Telecommand: '#268bd2',
})


class SessionScope(object):
    def __init__(self, sender):
        self.sender = sender

    def send(self, frame):
        self.sender.send(frame)


class Loop(object):
    def __init__(self, tasks, until=None):
        self.until = until
        self.tasks = tasks

    def _execute_once(self, session_scope):
        for step_no, step in enumerate(self.tasks):
            [telecommand, action_type] = step

            tokens = [
                (Token.String, "["),
                (Token.Timestamp, datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')),
                (Token.String, "] "),
                (Token.String, "Step "),
                (Token.CurrentStep, str(step_no + 1)),
                (Token.String, "/"),
                (Token.TotalSteps, str(len(self.tasks))),
                (Token.String, ": "),
                (Token.Action, action_type.__name__),
                (Token.String, "("),
                (Token.Telecommand, pprint.pformat(telecommand)),
                (Token.String, ")...\n")
            ]

            print_tokens(tokens, style=STYLE)

            action_type(telecommand).do(session_scope)

    def _eval_until(self):
        if self.until is None:
            return True

        return self.until()

    def __call__(self, session_scope):
        while True:
            self._execute_once(session_scope)

            if self._eval_until():
                break

