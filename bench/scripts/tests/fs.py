from bench_init import *


@make_test
def test_fs_download_file():
    # Request info about particular file
    assert_true(scripts.fs.get_file_info('telemetry.current'))

    from config import config

    # Download file
    scripts.fs.download_file('telemetry.current', 'downloaded.raw')
    os.path.isfile(os.path.join(config['files_path'], 'downloaded.raw'))


@make_test
def test_fs_list_file():
    # Request file list
    scripts.fs.list_files()

    # Request info about particular file
    assert_is_not_none(scripts.fs.get_file_info('telemetry.current'))

    # Request info about non-existing file
    assert_is_none(scripts.fs.get_file_info('aaabbbccc'))


@make_test
def test_fs_remove_file():
    # Request info about particular file
    assert_is_not_none(scripts.fs.get_file_info('telemetry.current'))

    # Remove file
    assert_true(scripts.fs.remove_file('telemetry.current'))

    # Request info about particular file - should be None
    assert_is_none(scripts.fs.get_file_info('telemetry.current'))

    # Remove file if exists
    assert_false(scripts.fs.remove_file('aabbcc'))

    # Remove non-existing file
    assert_false(scripts.fs.remove_file('aabbcc'))
