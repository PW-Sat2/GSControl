from colorama import Fore, Style

class Notes(list):
    def warning(self, text):
        self.append(Fore.YELLOW + '[Warning] ' + text + Style.RESET_ALL)

    def error(self, text):
        self.append(Fore.RED + '[Error] ' + text + Style.RESET_ALL)

    def info(self, text):
        self.append(Fore.CYAN + '[Info] ' + text + Style.RESET_ALL)