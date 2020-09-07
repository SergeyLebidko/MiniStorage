import os
from django.conf import settings


def get_tmp_folder_path():
    return str(settings.BASE_DIR) + settings.TMP_FOLDER


def get_tmp_file_path(filename):
    return get_tmp_folder_path() + filename


def check_tmp_folder():
    tmp_folder = get_tmp_folder_path()
    try:
        os.mkdir(tmp_folder)
    except OSError:
        pass
