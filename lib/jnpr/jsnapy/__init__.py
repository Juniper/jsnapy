# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

from .version import __version__
import ConfigParser
import os


def get_path(section, value):
    config = ConfigParser.ConfigParser({'config_file_path': '/etc/jsnapy', 'snapshot_path': '/etc/jsnapy/snapshots',
                                        'test_file_path': '/etc/jsnapy/testfiles', 'log_file_path': '/etc/logs/jsnapy'})
    config.read(os.path.join('/etc', 'jsnapy', 'jsnapy.cfg'))
    path = config.get(section, value)
    return path

from jnpr.jsnapy.jsnapy import SnapAdmin
