# coding=utf-8
import curses
import threading

from .colors import Colors

import os
os.environ['NCURSES_NO_UTF8_ACS'] = '1'

TICK = '#' #  '▇'


class MonitorUI:
    LOG_WINDOW_SIZE_SMALL = 32
    LOG_WINDOW_SIZE_BIG = 39

    def __init__(self, session, tasks, total_tasks, abortCallback, is_bound):
        self.isWorking = False
        self.session = session
        self.tasks = tasks
        self.total_tasks = total_tasks
        self.log_line = 0
        self.abortCallback = abortCallback
        self.colors = None
        self.paths = self._generatePaths(tasks)
        self.is_bound = is_bound
        self.first_line = 0
        self._is_incoming_frame_logged = False

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
            elif c == curses.KEY_RESIZE:
                self.stdscr.clear()
                maxY, maxX = self.stdscr.getmaxyx()
                self.initialize_windows()
                curses.doupdate()
            elif c == ord('a'):
                maxY, maxX = self.stdscr.getmaxyx()
                _, logX = self.logWindow.getmaxyx()
                self.log("MaxX = {}, MaxY = {}, LogX = {}".format(maxX, maxY, logX))
            elif c == curses.KEY_UP:
                self.first_line -= 1
                self._handle_list_scrolling()
            elif c == curses.KEY_DOWN:
                self.first_line += 1
                self._handle_list_scrolling()
            elif c == curses.KEY_NPAGE:
                maxY, _ = self.mainWindow.getmaxyx()
                self.first_line += maxY
                self._handle_list_scrolling()
            elif c == curses.KEY_PPAGE:
                maxY, _ = self.mainWindow.getmaxyx()
                self.first_line -= maxY
                self._handle_list_scrolling()
            elif c == ord('l'):
                self._is_incoming_frame_logged = not self._is_incoming_frame_logged

    def _handle_list_scrolling(self):
        maxY, _ = self.mainWindow.getmaxyx()
        max_start_line = max(0, len(self.tasks) - maxY)

        if self.first_line < 0:
            self.first_line = 0
        elif self.first_line > max_start_line:
            self.first_line = max_start_line

        self.update_tasklist(self.tasks)


    def _generate_header(self):
        self.header.addstr(1, 2, 'SESSION:')
        self.header.addstr(1, 11, '{}'.format(self.session), self.colors.YELLOW)
        if not self.is_bound:
            self.header.addstr(' UNBOUND', self.colors.RED)

        _, maxX = self.stdscr.getmaxyx()
        self.header.addstr(1, maxX - 18, 'Total tasks:')
        self.header.addstr(1, maxX - 5, '{:3d}'.format(self.total_tasks))

        self.header.addstr(1, maxX//2 - 11, 'Download tasks:')
        self.update_remaining()

    def _generatePaths(self,tasks):
        paths = {}
        for _, task in tasks.iteritems():
            paths[task.correlation_id] = task.file_name()
        return paths

    def update_remaining(self):
        _, maxX = self.stdscr.getmaxyx()
        self.header.addstr(1, maxX//2 + 5, '{:3d}'.format(len(self.tasks)), self.colors.GREEN)
        self.header.noutrefresh()

    def update_tasklist(self, tasks):
        self.tasks = tasks

        maxY, maxX = self.mainWindow.getmaxyx()
        self.mainWindow.move(0,0)

        x_download_counter = 23

        position = 0
        for index, (_, task) in enumerate(tasks.iteritems()):
            if index < self.first_line:
                continue
            self.mainWindow.addstr(position, 0, '{:3d} '.format(task.index), self.colors.CYAN)
            self.mainWindow.addstr('{:3d} '.format(task.correlation_id), self.colors.DYELLOW)
            self.mainWindow.clrtoeol()
            self.mainWindow.addstr(task.file_name(), self.colors.DBLUE)
            self.mainWindow.addstr(position, x_download_counter, '{:2d} '.format(len(task.chunks)), self.colors.YELLOW)

            graphLength = min(maxX - (x_download_counter + 3), len(task.chunks))
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
        maxY, _ = self.logWindow.getmaxyx()
        while self.log_line >= maxY:
            self.logWindow.scroll()
            self.log_line -= 1

    def _log_finish(self):
        self.log_line += 1
        self.logWindow.noutrefresh()
        self.header.noutrefresh()
        curses.doupdate()

    def _log_finish_no_advance(self):
        self.logWindow.noutrefresh()
        self.header.noutrefresh()
        curses.doupdate()

    def log(self, message):
        self._log_start()

        self.logWindow.addstr(self.log_line, 0, message)
        self._log_finish()

    def log_frame(self, downloadFrameView, stamp):
        if not self._is_incoming_frame_logged:
            return

        self._log_start()

        self.logWindow.addstr(self.log_line, 0, "{} ".format(stamp.strftime('%H:%M:%S')), self.colors.DCYAN)
        if downloadFrameView.is_success:
            self.logWindow.addstr("+ ", self.colors.GREEN)
        else:
            self.logWindow.addstr("- ", self.colors.RED)
        self.logWindow.addstr('{:3d} '.format(downloadFrameView.correlation_id), self.colors.DYELLOW)

        try:
            path = self.paths[downloadFrameView.correlation_id]
        except KeyError:
            path = "UNKNOWN"

        _, maxX = self.logWindow.getmaxyx()
        if maxX >= MonitorUI.LOG_WINDOW_SIZE_BIG:
            self.logWindow.addstr("{:18s} ".format(path), self.colors.DBLUE)
        elif maxX >= MonitorUI.LOG_WINDOW_SIZE_SMALL:
            path = path.replace("telemetry", "t")
            self.logWindow.addstr("{:11s} ".format(path), self.colors.DBLUE)

        self.logWindow.addstr('{:02d}'.format(downloadFrameView.chunk))
        self._log_finish()

    def log_filelist_frame(self, fileListFrameView, stamp):
        self._log_start()

        self.logWindow.addstr(self.log_line, 0, "{} ".format(stamp.strftime('%H:%M:%S')), self.colors.DCYAN)
        self.logWindow.addstr('{:3d} '.format(fileListFrameView.correlation_id), self.colors.DYELLOW)

        file_list_header = "FILE LIST"
        _, maxX = self.logWindow.getmaxyx()
        if maxX >= MonitorUI.LOG_WINDOW_SIZE_BIG:
            self.logWindow.addstr("{:18s} ".format(file_list_header), self.colors.YELLOW)
        elif maxX >= MonitorUI.LOG_WINDOW_SIZE_SMALL:
            self.logWindow.addstr("{:11s} ".format(file_list_header), self.colors.YELLOW)

        self.logWindow.addstr('{:02d}'.format(fileListFrameView.chunk))
        self._log_finish()

        for file_name, chunk_count in sorted(fileListFrameView.file_list.items()):
            self._log_filelist_item(file_name, chunk_count)

        self._log_finish_no_advance()  

    def _log_filelist_item(self, file_name, chunk_count):
        self._log_start()
        self.logWindow.addstr(self.log_line, 2, '{} '.format(file_name), self.colors.DBLUE)

        _, maxX = self.logWindow.getmaxyx()
        position = maxX - 4
        if maxX >= MonitorUI.LOG_WINDOW_SIZE_BIG:
            position = MonitorUI.LOG_WINDOW_SIZE_BIG - 8
        elif maxX >= MonitorUI.LOG_WINDOW_SIZE_SMALL:
            position = MonitorUI.LOG_WINDOW_SIZE_SMALL - 8

        self.logWindow.addstr(self.log_line, position, "{:3d} ".format(chunk_count), self.colors.DYELLOW)
        self.log_line += 1

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

