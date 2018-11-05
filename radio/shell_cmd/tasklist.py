from datetime import datetime

class DictWrapper(object):
    def __init__(self, d):
        self._d = d

    def __getattr__(self, name):
        return self._d[name]

def build(sender, rcv, frame_decoder, ns):
    def run(tasks):
        """
        Performs list of tasks.

        Each task is defined as list: [<telecommand object>, Send|SendReceive, "Wait|NoWait"]

        When using "Wait" it is necessary to type 'n<ENTER>' to continue running tasks
        """

        import pprint
        from prompt_toolkit.shortcuts import print_tokens
        from prompt_toolkit.styles import style_from_dict
        from pygments.token import Token

        style = style_from_dict({
            Token.Timestamp: '#fdf6e3',
            Token.CurrentStep: '#b58900',
            Token.TotalSteps: '#6c71c4',
            Token.Action: '#dc322f',
            Token.Telecommand: '#268bd2',
        })

        step_no = 0

        ns_wrapper = DictWrapper(ns)

        for [telecommand, action_type, wait] in tasks:
            step_no += 1

            tokens = [
                (Token.String, "["),
                (Token.Timestamp, datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')),
                (Token.String, "] "),
                (Token.String, "Step "),
                (Token.CurrentStep, str(step_no)),
                (Token.String, "/"),
                (Token.TotalSteps, str(len(tasks))),
                (Token.String, ": "),
                (Token.Action, action_type.__name__),
                (Token.String, "("),
                (Token.Telecommand, pprint.pformat(telecommand)),
                (Token.String, ")... ")
            ]

            print_tokens(tokens, style=style)

            action_type(telecommand).do(ns_wrapper)

            if wait is "NoWait":
                print_tokens([
                    (Token.String, "Done"),
                    (Token.String, "\n")
                ], style=style)
            else:
                print_tokens([
                    (Token.String, "Wait (type 'n' and press <Enter>)")
                ], style=style)

                user = ""
                while user[:1] != "n":
                    user = raw_input()
    
    return {
        'run': run
    }