# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

from .version import __version__
import ConfigParser
import os


def get_path(section, value):
    # config = ConfigParser.ConfigParser({'config_file_path': '/usr/local/share/', 'snapshot_path': '/usr/local/share/snapshots',
    #                                     'test_file_path': '/usr/local/share/testfiles', 'log_file_path': '/var/log/jsnapy'})
    config = ConfigParser.ConfigParser()
    config_location = os.path.join('/etc', 'jsnapy', 'jsnapy.cfg')
    if not os.path.isfile(config_location):
        raise Exception('Config file not found at %s '%config_location)
    config.read(config_location)
    # config.read(os.path.join('/usr/local/share', 'jsnapy', 'jsnapy.cfg'))
    path = config.get(section, value)
    return path

from jnpr.jsnapy.jsnapy import SnapAdmin
