# -*- coding: UTF-8 -*-
"""MongoDB driver module to insert tag data into NoSQL database."""
import inspect
import time
import os
import sys
import pathlib
from db.mongodb_api import MongoMedia
from lib import config
import lib.media_tools as media_tools
import lib.user_input as ui

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)

__all__ = ['insert_files_mongodb', 'insert_tags_mongodb', 'build_media_list']


def insert_files_mongodb(path_list: list, mongodb_api) -> None:
    """Inserts with metadata or the media files directly to MongoDB."""
    def_name = inspect.currentframe().f_code.co_name
    print(f"\n{def_name}()")
    try:
        for file_path in path_list:
            object_id = mongodb_api.store_bin_file(file_path)
            print(f"   adding: {object_id}")
        status = f"SUCCESS! {len(path_list)} files added\n"
    except (OSError, IOError) as exception:
        status = f"\n~!ERROR!~ {def_name}() {sys.exc_info()[0]}\n{exception}"
    print(status)


def insert_tags_mongodb(tag_list: list, mongodb_api) -> None:
    """Inserts with metadata or the media files directly to MongoDB."""
    def_name = inspect.currentframe().f_code.co_name
    print(f"\n{def_name}()")
    try:
        for tag_dict in tag_list:
            object_id = mongodb_api.upsert_single_tags('hash', tag_dict)
            print(f"   adding: {object_id}")
        status = f"SUCCESS! {len(tag_list)} media tags added"
    except (OSError, IOError) as exception:
        status = f"\n~!ERROR!~ {def_name}() {sys.exc_info()[0]}\n{exception}"
    print(status)


def build_media_list(input_path: pathlib.Path):
    """Find media files, parses tag data into list."""
    tag_list = []
    if input_path.exists() and input_path.is_dir():
        tag_list = media_tools.build_stat_list(input_path)[0]
    else:
        print(f"input path not found... {input_path}")
    return tag_list


def main():
    """Driver to insert tag/media into MongoDB."""
    print(f"{SCRIPT_NAME} starting...")
    start = time.perf_counter()
    config.show_header(SCRIPT_NAME)
    args = ui.get_cmd_args()
    path_list = [args.file_path]
    username = 'run_admin_run'
    password = 'run_pass_run'
    server = args.server
    port_num = args.port_num
    if config.DEMO_ENABLED:
        data_path = pathlib.Path(PARENT_PATH, 'data', 'input')
        # path_list = ui.prompt_path_input(input_path=data_path, skip_ui=True)
    else:
        path_list = ui.get_test_directories()
    for num, input_path in enumerate(path_list):
        if input_path.exists():
            # insert media files into media_db.media_lib (collection)
            mongodb_api = MongoMedia(server=server, port_num=port_num,
                                     username=username,
                                     password=password)
            if mongodb_api.is_connected():
                if not mongodb_api.is_admin_setup(username=username):
                    mongodb_api.add_admin(username=username,
                                          password=password)
                mongodb_api.drop_database()
                mongodb_api.show_database_status()
                print(f"\npath_{num:02d}: "
                      f"'{os.sep.join(input_path.parts[-3:])}'")
                media_tag_list = build_media_list(input_path)
                insert_tags_mongodb(media_tag_list, mongodb_api)
                media_paths = media_tools.get_all_media_paths(input_path)
                insert_files_mongodb(media_paths, mongodb_api)
                mongodb_api.show_database_status()
        else:
            print(f"input path not found... {input_path}")
    end = time.perf_counter() - start
    print(f"{SCRIPT_NAME} finished in {end:0.2f} seconds")


if __name__ == "__main__":
    main()
