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

TICK = '#'#'▇'

from enum import Enum
class Colors:
    def __init__(self):
        curses.init_pair(1,3,0)
        curses.init_pair(2,4,0)
        curses.init_pair(3,1,0)
        curses.init_pair(4,12,0)
        curses.init_pair(5,10,0)
        curses.init_pair(6,14,0)
        curses.init_pair(7,6,0)

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

    def _worker_thread(self, stdscr):
        curses.cbreak()
        curses.noecho()
        self.colors = Colors()
   
        self.stdscr = stdscr
        maxY, maxX = stdscr.getmaxyx()

        mainWidth = min(60, maxX) - 2

        self.mainWindowBox = stdscr.subwin(maxY-2, mainWidth+2, 2, 0)
        self.mainWindowBox.box()
        self.mainWindow = self.mainWindowBox.derwin(maxY-4, mainWidth,1,1)
        
        self.logWindowBox = stdscr.subwin(maxY-2, maxX - mainWidth - 3, 2, mainWidth + 2)
        self.logWindowBox.box()
        self.logWindow = self.logWindowBox.derwin(maxY-4, maxX - mainWidth - 5,1,1)
        self.logWindow.scrollok(True)
        self.logWidth = maxX - mainWidth - 5

        self.header = stdscr.subwin(3, maxX, 0, 0)
        self.header.box()

        self._generate_header()
        self.update_tasklist(self.tasks)

        self.mainWindowBox.refresh()
        self.logWindowBox.refresh()
        self.header.refresh()

        while self.isWorking:
            sleep(1)
            c = stdscr.getch()
            if c == ord('q') or c == 3:
                self.abortCallback()
                break

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
        self.header.refresh()

    def update_tasklist(self, tasks):
        self.tasks = tasks

        maxY, maxX = self.mainWindow.getmaxyx()

        position = 0
        for _, task in tasks.iteritems():
            self.mainWindow.addstr(position, 1, '{:3d}'.format(task.correlation_id()), self.colors.DYELLOW)
            self.mainWindow.clrtoeol()
            self.mainWindow.addstr(position, 5, task._path[1:], self.colors.DRED)
            self.mainWindow.addstr(position, 24, '{:2d}'.format(len(task._seqs)), self.colors.YELLOW)

            graphLength = min(maxX - 31, len(task._seqs))
            bar = TICK * graphLength
            self.mainWindow.addstr(position, 28, bar)

            position+=1
            if position > maxY - 1:
                    break

        self.mainWindow.clrtobot()
        self.mainWindow.refresh()
        self.update_remaining()

    def _log_start(self):     
        maxY, maxX = self.logWindow.getmaxyx()
        if self.log_line >= maxY:
            self.logWindow.scroll()
            self.log_line -= 1

    def _log_finish(self):
        self.log_line += 1
        self.logWindow.refresh()
        self.header.refresh()

    def log(self, message):
        print(message)
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
        self.logWindow.addstr(path, self.colors.DRED)
        self.logWindow.addstr(self.log_line, 35, '{:02d}'.format(downloadFrame._seq))
        self._log_finish()

    def _curses_thread(self):
        curses.wrapper(self._worker_thread)

    def stop(self):
        self.isWorking = False

    def update_remaining_tasks(self, tasklist):
        _, maxX = self.stdscr.getmaxyx()
        self.header.addstr(1, maxX//2 + 5, '{:d}'.format(len(tasklist)), self.colors.RED)
        self.header.refresh()

    def run(self):
        self.isWorking = True
        listener_thread = threading.Thread(target=self._curses_thread)
        listener_thread.start()
        return listener_thread

