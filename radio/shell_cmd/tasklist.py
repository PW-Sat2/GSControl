from threading import Timer
from datetime import datetime
from radio.task_actions import WaitMode
import sys
import telecommand as tc


def custom_raw_input(text=""):
    sys.stdout.write(text)
    return sys.stdin.readline().strip()

class DictWrapper(object):
    def __init__(self, d):
        self._d = d

    def __getattr__(self, name):
        return self._d[name]

def build(sender, rcv, frame_decoder, analyzer, ns):
    import pprint
    from prompt_toolkit.shortcuts import print_tokens
    from prompt_toolkit.styles import style_from_dict
    from pygments.token import Token
    from monitor import MonitorConnector

    def sendExtraCommand(style, ns_wrapper, command):
        from radio.task_actions import Send
        [telecommand, action_type] = [command, Send]

        tokens = [
            (Token.String, "["),
            (Token.Timestamp, datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')),
            (Token.String, "] "),
            (Token.CurrentStep, "Extra"),
            (Token.String, ": "),
            (Token.Action, action_type.__name__),
            (Token.String, "("),
            (Token.Telecommand, pprint.pformat(telecommand)),
            (Token.String, ")... Please repeat: "),
        ]

        print_tokens(tokens, style=style)
        action_type(telecommand).do(ns_wrapper)

    def send_additional_beacon(style, ns_wrapper):
        import telecommand as tc
        sendExtraCommand(style, ns_wrapper, tc.SendBeacon())

    def get_and_send_missing_chunks_command(style, ns_wrapper, telecommand, monitorConnector):
        newCommand = monitorConnector.get_missings_for_command(telecommand)
        if not newCommand:
            print("Not found.")
            return 

        sendExtraCommand(style, ns_wrapper, newCommand)

    def add_missings_to_tasklist(style, ns_wrapper, tasks, monitorConnector):
        import telecommand as tc
        from radio.task_actions import SendLoop, WaitMode

        newTasks = monitorConnector.get_additional_tasks()
        if not newTasks or len(newTasks) == 0:
            print("Not found.")
            return 

        tasks.append([[tc.SendBeacon(), 20], SendLoop, WaitMode.NoWait])

        #     get_and_send_missing_chunks_command(style, ns_wrapper, tasks, step_no - 1)
        #     continue
        # elif user_input == 't':
        #     add_missings_to_tasklist(style, ns_wrapper, tasks)

    def run(tasks, start_from=1):
        """
        Performs list of tasks.

        Each task is defined as list: [<arg>, Send|SendReceive|Sleep|Print, WaitMode.Wait|WaitMode.NoWait]
        
        For Send <arg> is a telecommand object
        For SendReceive <arg> is a telecommand object
        For Sleep <arg> is time in seconds
        For Print <arg> is text to display

        When using "Wait" it is necessary to type 'n<ENTER>' to continue running tasks
        """     

        style = style_from_dict({
            Token.Timestamp: '#fdf6e3',
            Token.CurrentStep: '#b58900',
            Token.TotalSteps: '#6c71c4',
            Token.Action: '#dc322f',
            Token.Telecommand: '#268bd2',
        })

        ns_wrapper = DictWrapper(ns)
        monitorConnector = MonitorConnector()

        step_no = start_from - 1

        try:
            while step_no < len(tasks) and step_no >= 0:
                [telecommand, action_type, wait] = tasks[step_no]

                tokens = [
                    (Token.String, "["),
                    (Token.Timestamp, datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')),
                    (Token.String, "] "),
                    (Token.String, "Step "),
                    (Token.CurrentStep, str(step_no + 1)),
                    (Token.String, "/"),
                    (Token.TotalSteps, str(len(tasks))),
                    (Token.String, ": "),
                    (Token.Action, action_type.__name__),
                    (Token.String, "("),
                    (Token.Telecommand, pprint.pformat(telecommand)),
                    (Token.String, ")... ")
                ]

                print_tokens(tokens, style=style)

                def write_end():
                    sys.stdout.write("[X] ")
                    sys.stdout.flush()

                timer_WriteProgramPart = Timer(7, write_end)
                if isinstance(telecommand, tc.WriteProgramPart):
                    timer_WriteProgramPart.start()

                action_type(telecommand).do(ns_wrapper)

                if wait is WaitMode.NoWait:
                    print_tokens([
                        (Token.String, "Done"),
                        (Token.String, "\n")
                    ], style=style)
                else:
                    print_tokens([
                        (Token.String, "Wait ")
                    ], style=style)

                    while True:
                        user_input = custom_raw_input()
                        timer_WriteProgramPart.cancel()
                        if user_input == 'n':
                            break
                        elif user_input == 'r':
                            step_no -= 1
                            break
                        elif user_input == 'p':
                            step_no -= 2
                            break
                        elif user_input[:1] >= '0' and user_input[:1] <= '9':
                            user_step_no = -1
                            try:
                                user_step_no = int(user_input)
                            except ValueError:
                                pass
                            if user_step_no > -1:
                                step_no = user_step_no - 2
                                break
                        elif user_input == 'b':
                            send_additional_beacon(style, ns_wrapper)
                            continue
                        elif user_input == 'm':
                            get_and_send_missing_chunks_command(style, ns_wrapper, tasks[step_no][0], monitorConnector)
                            continue
                        elif user_input == 't':
                            add_missings_to_tasklist(style, ns_wrapper, tasks)
                            continue
                        elif user_input == 'q':
                            return

                        print_tokens([
                            (Token.Action, "Unknown command '{}'. ".format(user_input)),
                            (Token.String, "Please repeat: "),
                            ], style=style)
                step_no += 1
        except KeyboardInterrupt:
            print_tokens([
                (Token.String, "\n"),
                (Token.Action, "Aborted."),
                (Token.String, "\n")
            ], style=style)
            pass
    
    def analyze(tasks):
        analyzer.run(tasks)

    def monitor(tasks):
        from monitor import Monitor
        monitor = Monitor(rcv, frame_decoder)
        return monitor.run(tasks)
    
    def load(tasks_file_path, silent=False):
        tasks = analyzer.load(tasks_file_path)
        with open(tasks_file_path, 'r') as input_file:
            if not silent:
                print input_file.read()
            else:
                pass
        return tasks

    def panic_detumbling():
        detumbling = load('panic/detumbling.py', silent=True)
        run(detumbling)

    def panic_power_cycle():
        power_cycle = load('panic/power_cycle.py', silent=True)
        run(power_cycle)

    return {
        'run': run,
        'analyze': analyze,
        'load': load,
        'panic_power_cycle': panic_power_cycle,
        'panic_detumbling': panic_detumbling,
        'monitor': monitor
    }