#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import os
import yaml
import logging.config
from jnpr.jsnapy import get_config_location
from jnpr.jsnapy import get_path
from jnpr.jsnapy import venv_check
import sys


def setup_logging(
    default_path="logging.yml", default_level=logging.INFO, env_key="LOG_CFG"
):
    config_location = get_config_location("logging.yml")
    path = os.path.join(config_location, default_path)
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    ###################################
    # Creating Folder path for SNAPSHOT
    ###################################
    # Modified by @gcasella to use the function created on lines 24-29 in the __init__.py.
    if "win32" not in sys.platform and not venv_check:
        snapshots_path = get_path("DEFAULT", "snapshot_path")
        snapshots_path = os.path.expanduser(snapshots_path)
        if not os.path.isdir(snapshots_path):
            os.makedirs(snapshots_path)

    HOME = os.path.expanduser("~")  # correct cross platform way to do it
    home_folder = os.path.join(HOME, ".jsnapy")
    if not os.path.isdir(home_folder):
        os.mkdir(home_folder)
