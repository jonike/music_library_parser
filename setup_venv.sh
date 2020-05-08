#!/bin/bash
## Requirements: python-pip, virtualenv
## Create a virtualenv, and activate:
sudo apt-get install libpq-dev python-dev
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
