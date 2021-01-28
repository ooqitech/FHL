import datetime
import os


def format_time(dt):
    """时间格式化"""
    if isinstance(dt, datetime.datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt


def parse_time(dt_str):
    if isinstance(dt_str, str):
        return datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    return None


def get_file_create_time(file_path):
    assert os.path.exists(file_path)
    return datetime.datetime.fromtimestamp(os.path.getctime(file_path))


def get_file_modify_time(file_path):
    assert os.path.exists(file_path)
    return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))


def get_tomorrow():
    return (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y%m%d')
