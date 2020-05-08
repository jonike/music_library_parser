# -*- coding: UTF-8 -*-
"""UI module to parse user input."""
import argparse
import inspect
import os
import pathlib
from pathvalidate.argparse import sanitize_filepath_arg

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)
TWO_PARENT_PATH = os.sep.join(pathlib.Path(BASE_DIR).parts[:-2])

__all__ = ['get_cmd_args', 'get_test_directories', 'prompt_path_input']


def get_cmd_args() -> list:
    """Command line input on directory to scan recursively for media files."""
    def_name = inspect.currentframe().f_code.co_name
    parser = argparse.ArgumentParser(description='media_db_parser')
    parser.add_argument("-s", "--server",
                        type=str, default='localhost',
                        help="server")
    parser.add_argument("-p", "--port_num",
                        type=int, default=27017,
                        help="port_num")
    parser.add_argument("-f", "--file_path",
                        type=sanitize_filepath_arg,
                        help="file_path")
    args = parser.parse_args()
    if args.file_path is None:
        args.file_path = pathlib.Path(TWO_PARENT_PATH, 'data', 'input')
    else:
        args.file_path = pathlib.Path(args.file_path)
        if args.file_path.exists() and args.file_path.is_dir():
            print(f"{def_name}() dumping path:'{str(args.file_path)}'")
        else:
            parser.error(f"invalid path: '{str(args.file_path)}'")
            args.file_path = None
    return args


def get_test_directories() -> list:
    """Scans test directories recursively for media files."""
    def_name = inspect.currentframe().f_code.co_name
    # option if reporting on several directories
    base_drive = 'D:'
    folder_list = ['!FLAC_TEST0', '!FLAC_TEST1', '!Master_Music']
    path_list = [pathlib.Path(base_drive, subdir) for subdir in folder_list]
    print(f"{def_name}()\n",
          f"parsing '{len(path_list)}' path(s)")
    return path_list


def prompt_path_input(input_path: pathlib.Path, skip_ui: bool = True) -> list:
    """Prompts user for which directory to scan recursively for media files."""
    def_name = inspect.currentframe().f_code.co_name
    if not skip_ui:
        input_path = pathlib.Path(input("enter valid path: ").strip())
    if input_path.exists() and input_path.is_dir():
        print(f"{def_name}()\n",
              f"skip_ui: {str(skip_ui).upper()}",
              f"parsing '{input_path}'")
    else:
        print(f"ERROR: invalid path: '{str(input_path)}'")
        input_path = None
    return [input_path]
