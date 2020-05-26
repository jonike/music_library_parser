# -*- coding: UTF-8 -*-
"""Python module to show packages installed on host."""
import os
import time
from lib import config

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)


def main():
    """Driver to display installed python packages."""
    print(f"{SCRIPT_NAME} starting...")
    start = time.perf_counter()
    config.show_header(SCRIPT_NAME)
    config.show_packages()
    end = time.perf_counter() - start
    print(f"\n{SCRIPT_NAME} finished in {end:0.2f} seconds")


if __name__ == "__main__":
    main()
