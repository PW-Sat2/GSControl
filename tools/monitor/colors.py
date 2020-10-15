import curses
import os
import json

class Colors:
    def __init__(self):
        self._config = self._try_load_configuration()
        self._define_default_colors()

        self.DCYAN = self._get_color('DCYAN', 1)
        self.DRED = self._get_color('DRED', 2)
        self.DBLUE = self._get_color('DBLUE', 3)
        self.RED = self._get_color('RED', 4)
        self.GREEN = self._get_color('GREEN', 5)
        self.YELLOW = self._get_color('YELLOW', 6)
        self.DYELLOW = self._get_color('DYELLOW', 7)
        self.CYAN = self._get_color('CYAN', 8)

    def _try_load_configuration(self):
        config_file_name = 'monitor_colors.json'
        path = os.path.join(os.getcwd(), config_file_name)
        if not os.path.isfile(path):
            return None

        with open(path, 'r') as f:
            data = json.load(f)
            return data

    def _define_default_colors(self):
        curses.init_pair(1,curses.COLOR_CYAN,0)
        curses.init_pair(2,curses.COLOR_RED,0)

        if curses.COLORS > 8:
            if curses.COLORS > 16: # Win10 - 768
                curses.init_color(20, 0 ,0 ,850)
                curses.init_pair(3,20 , -1)
            else:  # Win7 - 16
                curses.init_pair(3,curses.COLOR_BLUE + 8, -1)
            curses.init_pair(4,curses.COLOR_RED + 8,-1)
            curses.init_pair(5,curses.COLOR_GREEN + 8,-1)
            curses.init_pair(6,curses.COLOR_YELLOW + 8,-1)
            curses.init_pair(7,curses.COLOR_BLACK + 8,-1)
            curses.init_pair(8,curses.COLOR_CYAN + 8,-1)
        else:
            curses.init_pair(3,curses.COLOR_BLUE, -1)
            curses.init_pair(4,curses.COLOR_RED,-1)
            curses.init_pair(5,curses.COLOR_GREEN,-1)
            curses.init_pair(6,curses.COLOR_YELLOW,-1)
            curses.init_pair(7,curses.COLOR_GREEN,-1)
            curses.init_pair(8,curses.COLOR_CYAN,-1)

    def _get_color(self, color_name, default_index):
        if self._config is None or color_name not in self._config or curses.COLORS <= 16:
            return curses.color_pair(default_index)

        color_data = self._config.get(color_name, [])
        new_color_index = 30 + default_index

        r, g, b = self._decode_color_data(color_data)

        curses.init_color(new_color_index, r, g, b)
        curses.init_pair(default_index,new_color_index , -1)
        return curses.color_pair(default_index)
    
    def _decode_color_data(self, color_data):
        if len(color_data) != 3:
            return 500, 500, 500

        r = color_data[0] * 1000 / 255
        g = color_data[1] * 1000 / 255
        b = color_data[2] * 1000 / 255

        return r, g, b
