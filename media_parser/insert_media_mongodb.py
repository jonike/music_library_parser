# -*- coding: UTF-8 -*-
"""MongoDB driver module to insert tag data into NoSQL database."""
import inspect
import time
import os
import sys
from pathlib import Path
from lib import config, user_input, media_tools
from db import mongodb_api, cmd_args

MODULE_NAME = Path(__file__).resolve().name
BASE_DIR = Path.cwd()
PARENT_PATH = Path.cwd().parent

__all__ = ['insert_files_mongodb', 'insert_tags_mongodb', 'build_media_list']


def insert_files_mongodb(path_list: list, mdb) -> None:
    """Inserts media files ('.mp3', '.m4a', etc.) into MongoDB."""
    func_name = f"{inspect.currentframe().f_code.co_name}()"
    print(f"\n{func_name}")
    try:
        for file_path in path_list:
            object_id = mdb.store_bin_file(file_path)
            print(f"   adding: {object_id}")
        status = f"SUCCESS! {len(path_list)} files added\n"
    except (OSError, IOError) as ex:
        status = f"\n~!ERROR!~ {func_name}() {sys.exc_info()[0]}\n{ex}"
    print(status)


def insert_tags_mongodb(tag_list: list, mdb) -> None:
    """Inserts media metadata (tag data) into MongoDB."""
    func_name = f"{inspect.currentframe().f_code.co_name}()"
    print(f"\n{func_name}")
    try:
        for tag_dict in tag_list:
            object_id = mdb.upsert_single_tags('hash', tag_dict)
            print(f"   adding: {object_id}")
        status = f"SUCCESS! {len(tag_list)} media tags added"
    except (OSError, IOError) as ex:
        status = f"\n~!ERROR!~ {func_name} {sys.exc_info()[0]}\n{ex}"
    print(status)


def build_media_list(input_path: Path):
    """Find media files, parses tag data into list."""
    tag_list = []
    if input_path.exists() and input_path.is_dir():
        tag_list = media_tools.build_stat_list(input_path)[0]
    else:
        print(f"input path not found... {input_path}")
    return tag_list


def main():
    """Driver to insert tag/media into MongoDB media_db instance."""
    print(f"{MODULE_NAME} starting...")
    start = time.perf_counter()
    config.show_header(MODULE_NAME)
    args = cmd_args.get_cmd_args(port_num=27017)
    path_list = [args.file_path]
    server = args.server
    port_num = args.port_num
    database = args.database
    username = args.username
    password = args.password
    if config.DEMO_ENABLED:
        data_path = Path(BASE_DIR, 'data', 'input')
        path_list = user_input.prompt_path_input(input_path=data_path,
                                                 skip_ui=True)
    else:
        path_list = user_input.get_test_directories()
    for num, input_path in enumerate(path_list):
        if input_path.exists():
            # insert media files into media_db.media_lib (collection)
            mdb = mongodb_api.MongoMedia(server=server,
                                         port_num=port_num,
                                         database=database,
                                         username=username,
                                         password=password)
            if mdb.is_connected():
                if not mdb.is_admin_setup(username=username):
                    mdb.add_admin(username=username,
                                  password=password)
                mdb.drop_database()
                mdb.show_database_status()
                print(f"\npath_{num:02d}: "
                      f"'{os.sep.join(input_path.parts[-3:])}'")
                media_tag_list = build_media_list(input_path)
                insert_tags_mongodb(media_tag_list, mdb)
                media_paths = media_tools.get_all_media_paths(input_path)
                insert_files_mongodb(media_paths, mdb)
                mdb.show_database_status()
        else:
            print(f"input path not found... {input_path}")
    end = time.perf_counter() - start
    print(f"{MODULE_NAME} finished in {end:0.2f} seconds")


if __name__ == "__main__":
    main()
