import os


def parse_photo(ground_filename):
    from config import config

    with open(os.path.join(config['files_path'], ground_filename), 'rb') as f:
        data_string = f.read()

    data_string = data_string[4:]
    result = ""
    while len(data_string) > 0:
        part = data_string[0:512 - 6]

        result += part
        data_string = data_string[512:]
        data_string = data_string[0:]

    with open(os.path.join(config['files_path'], ground_filename + ".jpg"), 'wb') as f:
        f.write(result)
