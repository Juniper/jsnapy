#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import os
import sys
import yaml
import logging.config
from jnpr.jsnapy import get_config_location
from six import iteritems

def setup_logging(
        default_path='logging.yml', default_level=logging.INFO,
        env_key='LOG_CFG'):
    config_location = get_config_location('logging.yml')
    path = os.path.join(config_location, default_path)
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
            for (handler, value) in iteritems(config['handlers']):
                if handler == 'console':
                    pass
                else:
                    if hasattr(sys, 'real_prefix'):
                        value['filename'] = (os.path.join
                                             (sys.prefix,
                                              'var/logs/jsnapy/jsnapy.log'))
                    elif 'win' in sys.platform:
                        value['filename'] = (os.path.join
                                             (os.path.expanduser('~'),
                                              'logs\jsnapy\jsnapy.log'))

                with open(path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
