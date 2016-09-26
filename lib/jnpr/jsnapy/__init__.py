# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

from .version import __version__
import ConfigParser
import os
import colorama
colorama.init(autoreset=True)


def get_path(section, value):
    # config = ConfigParser.ConfigParser({'config_file_path': '/usr/local/share/', 'snapshot_path': '/usr/local/share/snapshots',
    #                                     'test_file_path': '/usr/local/share/testfiles', 'log_file_path': '/var/log/jsnapy'})
    config = ConfigParser.ConfigParser()
    config_location = None
    
    p_locations = []
    if 'JSNAPY_HOME' in os.environ:
        p_locations = [os.environ['JSNAPY_HOME']]   
    p_locations.extend(['~/.jsnapy','/etc/jsnapy'])
    
    for loc in p_locations:
        possible_location =  os.path.join(loc,'jsnapy.cfg')
        if os.path.isfile(possible_location):
            config_location = possible_location
            break
    
    if config_location is None:
        raise Exception('Config file not found at {0}'.format(repr(p_locations)))
    config.read(config_location)
    # config.read(os.path.join('/usr/local/share', 'jsnapy', 'jsnapy.cfg'))
    path = config.get(section, value)
    return path

from jnpr.jsnapy.jsnapy import SnapAdmin
