class File:
    TASKS_LIST = "tasks"

    @classmethod
    def valid(self, file_path):
        with open(file_path) as tasks_file:
            tasks_find = tasks_file.readline().find(self.TASKS_LIST)
            tasks_file.close()
            if tasks_find != 0:
                return False
        return True
