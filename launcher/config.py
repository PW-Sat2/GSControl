class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


config = AttrDict(
    base_path = '/home/sat_user/',
    gnu_radio_folder = 'gr-new/',
    gscontrol_main_path = 'gs/GSControl/radio/radio_comm.py',
    gscontrol_config_path = 'gs/config.py',
    gs_launcher_script_relative_path = 'launcher',
)