# coding=utf-8
import curses
import threading
from colorama import Fore, Style, Back
from time import sleep

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../PWSat2OBC/integration_tests'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import response_frames

os.environ['NCURSES_NO_UTF8_ACS'] = '1'

TICK = '#'#'▇'

from enum import Enum
class Colors:
    def __init__(self):
        curses.init_pair(1,curses.COLOR_CYAN,0)
        curses.init_pair(2,curses.COLOR_RED,0)

        if curses.COLORS > 8:
            curses.init_color(20, 0 ,0 ,700)
            curses.init_pair(3,20 , -1)
            curses.init_pair(4,curses.COLOR_RED + 8,-1)
            curses.init_pair(5,curses.COLOR_GREEN + 8,-1)
            curses.init_pair(6,curses.COLOR_YELLOW + 8,-1)
            curses.init_pair(7,curses.COLOR_BLACK + 8,-1)
        else:
            curses.init_pair(3,curses.COLOR_BLUE, -1)
            curses.init_pair(4,curses.COLOR_RED,-1)
            curses.init_pair(5,curses.COLOR_GREEN,-1)
            curses.init_pair(6,curses.COLOR_YELLOW,-1)
            curses.init_pair(7,curses.COLOR_GREEN,-1)

        self.DCYAN = curses.color_pair(1)
        self.DRED = curses.color_pair(2)
        self.DBLUE = curses.color_pair(3)
        self.RED = curses.color_pair(4)
        self.GREEN = curses.color_pair(5)
        self.YELLOW = curses.color_pair(6)
        self.DYELLOW = curses.color_pair(7)

class MonitorUI:
    def __init__(self, session, tasks, total_tasks, abortCallback):
        self.isWorking = False
        self.session = session
        self.tasks = tasks
        self.total_tasks = total_tasks
        self.log_line = 0
        self.abortCallback = abortCallback
        self.colors = None
        self.paths = self._generatePaths(tasks)

    def initialize_windows(self):
        maxY, maxX = self.stdscr.getmaxyx()
        maxMainWidth = min(60, maxX//2) - 2
        mainWidth = max(43, maxMainWidth)

        logWidth = maxX - mainWidth - 2

        self.mainWindowBox = self.stdscr.subwin(maxY-2, mainWidth+2, 2, 0)
        self.mainWindowBox.box()
        self.mainWindow = self.mainWindowBox.derwin(maxY-4, mainWidth,1,1)
        
        self.logWindowBox = self.stdscr.subwin(maxY-2, logWidth, 2, mainWidth + 2)
        self.logWindowBox.box()
        self.logWindow = self.logWindowBox.derwin(maxY-4, logWidth - 2,1,1)
        self.logWindow.scrollok(True)
        self.logWidth = maxX - mainWidth - 5

        self.header = self.stdscr.subwin(3, maxX, 0, 0)
        self.header.box()

        self._generate_header()
        self.update_tasklist(self.tasks)

        self.mainWindowBox.noutrefresh()
        self.logWindowBox.noutrefresh()
        self.header.noutrefresh()
        curses.doupdate()

    def _worker_thread(self, stdscr):
        curses.cbreak()
        curses.noecho()
        curses.use_default_colors()
        self.colors = Colors()
        curses.halfdelay(3)
   
        self.stdscr = stdscr
        self.initialize_windows()
        self.log("Loaded {} tasks.".format(len(self.tasks)))

        while self.isWorking:
            c = stdscr.getch()
            if c == ord('q') or c == 3 or c == 27:
                break
            if c == curses.KEY_RESIZE:
                self.stdscr.clear()
                maxY, maxX = self.stdscr.getmaxyx()
                self.initialize_windows()
                curses.doupdate()
            if c == ord('a'):
                maxY, maxX = self.stdscr.getmaxyx()
                self.log("MaxX = {}, MaxY = {}".format(maxX, maxY))

    def _generate_header(self):
        self.header.addstr(1, 2, 'SESSION:')
        self.header.addstr(1, 11, '{}'.format(self.session), self.colors.YELLOW)

        _, maxX = self.stdscr.getmaxyx()
        self.header.addstr(1, maxX - 18, 'Total tasks:')
        self.header.addstr(1, maxX - 5, '{:3d}'.format(self.total_tasks))

        self.header.addstr(1, maxX//2 - 11, 'Download tasks:')
        self.update_remaining()

    def _generatePaths(self,tasks):
        paths = {}
        for _, task in tasks.iteritems():
            paths[task.correlation_id()] = task._path[1:]
        return paths

    def update_remaining(self):
        _, maxX = self.stdscr.getmaxyx()
        self.header.addstr(1, maxX//2 + 5, '{:3d}'.format(len(self.tasks)), self.colors.GREEN)
        self.header.noutrefresh()

    def update_tasklist(self, tasks):
        self.tasks = tasks

        maxY, maxX = self.mainWindow.getmaxyx()
        self.mainWindow.move(0,0)

        position = 0
        for _, task in tasks.iteritems():
            self.mainWindow.addstr(position, 1, '{:3d}'.format(task.correlation_id()), self.colors.DYELLOW)
            self.mainWindow.clrtoeol()
            self.mainWindow.addstr(position, 5, task._path[1:], self.colors.DBLUE)
            self.mainWindow.addstr(position, 24, '{:2d} '.format(len(task._seqs)), self.colors.YELLOW)

            graphLength = min(maxX - 27, len(task._seqs))
            bar = TICK * graphLength

            try:
                self.mainWindow.addstr(bar)
            except curses.error:
                # hack for allowing inserting characer to bottom right position.
                pass

            position+=1
            if position > maxY - 1:
                    break

        if position < maxY:
            self.mainWindow.clrtobot()
        self.mainWindow.noutrefresh()
        self.update_remaining()
        curses.doupdate()

    def _log_start(self):     
        maxY, maxX = self.logWindow.getmaxyx()
        while self.log_line >= maxY:
            self.logWindow.scroll()
            self.log_line -= 1

    def _log_finish(self):
        self.log_line += 1
        self.logWindow.noutrefresh()
        self.header.noutrefresh()
        curses.doupdate()

    def log(self, message):
        self._log_start()

        self.logWindow.addstr(self.log_line, 1, message)
        self._log_finish()

    def logFrame(self, downloadFrame, stamp):
        self._log_start()

        self.logWindow.addstr(self.log_line, 1, "{} ".format(stamp.strftime('%H:%M:%S')), self.colors.DCYAN)
        if isinstance(downloadFrame, response_frames.common.FileSendErrorFrame):
            self.logWindow.addstr("- ", self.colors.RED)
        else:
            self.logWindow.addstr("+ ", self.colors.GREEN)
        self.logWindow.addstr('{:3d} '.format(downloadFrame.correlation_id), self.colors.DYELLOW)

        try:
            path = self.paths[downloadFrame.correlation_id]
        except KeyError:
            path = "UNKNOWN"

        _, maxX = self.logWindow.getmaxyx()
        if maxX >= 40:
            self.logWindow.addstr("{:18s} ".format(path), self.colors.DBLUE)
        elif maxX >= 33:
            path = path.replace("telemetry", "t")
            self.logWindow.addstr("{:11s} ".format(path), self.colors.DBLUE)

        self.logWindow.addstr('{:02d}'.format(downloadFrame._seq))
        self._log_finish()

    def _curses_thread(self):
        try:
            curses.wrapper(self._worker_thread)
        finally:
            self.stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
        self.abortCallback()

    def stop(self):
        self.isWorking = False

    def run(self):
        self.isWorking = True
        listener_thread = threading.Thread(target=self._curses_thread)
        listener_thread.start()
        return listener_thread

