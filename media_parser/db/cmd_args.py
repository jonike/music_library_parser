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

__all__ = ['get_cmd_args']


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
    parser.add_argument("-d", "--database",
                        type=str, default='media_db',
                        help="database")
    parser.add_argument("-f", "--file_path",
                        type=sanitize_filepath_arg,
                        help="username")
    parser.add_argument("-u", "--username",
                        type=str, default='run_admin_run',
                        help="file_path")
    parser.add_argument("-w", "--password",
                        type=str, default='run_pass_run',
                        help="password")
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
