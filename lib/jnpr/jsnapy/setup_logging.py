#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import os
import yaml
import logging.config
from jnpr.jsnapy import get_config_location


def setup_logging(
        default_path='logging.yml', default_level=logging.INFO, env_key='LOG_CFG'):
    config_location = get_config_location('logging.yml')
    path = os.path.join(config_location, default_path)
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
