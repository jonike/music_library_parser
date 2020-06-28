# -*- coding: UTF-8 -*-
"""Python module to show packages installed on host."""
import os
import time
from lib import config

BASE_DIR, MODULE_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)


def main():
    """Driver to display installed python packages."""
    print(f"{MODULE_NAME} starting...")
    start = time.perf_counter()
    config.show_header(MODULE_NAME)
    config.show_packages()
    end = time.perf_counter() - start
    print(f"\n{MODULE_NAME} finished in {end:0.2f} seconds")


if __name__ == "__main__":
    main()
