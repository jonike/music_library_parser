# -*- coding: UTF-8 -*-
"""UI module to parse user input."""
import argparse
import inspect
from pathlib import Path
from pathvalidate.argparse import sanitize_filepath_arg

MODULE_NAME = Path(__file__).resolve().name
BASE_DIR = Path.cwd()
PARENT_PATH = Path.cwd().parent
TWO_PARENT_PATH = Path.cwd().parent.parent

__all__ = ['get_cmd_args']


def get_cmd_args(port_num: int = 27017) -> list:
    """Command line input on directory to scan recursively for media files."""
    def_name = inspect.currentframe().f_code.co_name
    parser = argparse.ArgumentParser(description='media_db_parser')
    parser.add_argument("-s", "--server",
                        type=str, default='localhost',
                        help="server")
    parser.add_argument("-p", "--port_num",
                        type=int, default=port_num,
                        help="port_num")  # 5433 5432 27017 27018
    parser.add_argument("-d", "--database",
                        type=str, default='media_db',
                        help="database")
    parser.add_argument("-f", "--file_path",
                        default=Path(TWO_PARENT_PATH, 'data', 'input'),
                        type=sanitize_filepath_arg,
                        help="username")
    parser.add_argument("-u", "--username",
                        type=str, default='run_admin_run',
                        help="file_path")
    parser.add_argument("-w", "--password",
                        type=str, default='run_pass_run',
                        help="password")
    args = parser.parse_args()
    args.file_path = Path(args.file_path)
    if args.file_path.exists() and args.file_path.is_dir():
        print(f"{def_name}() dumping path:'{args.file_path}'")
    else:
        parser.error(f"invalid path: '{args.file_path}'")
        args.file_path = None
    return args
