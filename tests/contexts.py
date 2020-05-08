# -*- coding: UTF-8 -*-
import sys
import os

BASE_DIR, SCRIPT_NAME = os.path.split(os.path.abspath(__file__))
PARENT_PATH, CURR_DIR = os.path.split(BASE_DIR)

parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(PARENT_PATH, 'media_parser'))
sys.path.insert(0, os.path.join(PARENT_PATH, 'tests'))
print("\n".join(sys.path))
