# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

from .version import __version__
import ConfigParser
import os

def get_config_location(file='jsnapy.cfg'):
    p_locations = []
    if 'JSNAPY_HOME' in os.environ:
        p_locations = [os.environ['JSNAPY_HOME']]   
    p_locations.extend([os.path.join(os.path.expanduser('~'),'.jsnapy'),'/etc/jsnapy'])
    
    for loc in p_locations:
        possible_location =  os.path.join(loc,file)
        if os.path.isfile(possible_location):
            return loc
    return None
    

def get_path(section, value):
    # config = ConfigParser.ConfigParser({'config_file_path': '/usr/local/share/', 'snapshot_path': '/usr/local/share/snapshots',
    #                                     'test_file_path': '/usr/local/share/testfiles', 'log_file_path': '/var/log/jsnapy'})
    config = ConfigParser.ConfigParser()
    
    config_location = get_config_location()
    if config_location is None:
        raise Exception('Config file not found')
    config_location = os.path.join(config_location,'jsnapy.cfg')
    config.read(config_location)
    path = config.get(section, value)
    return path

from jnpr.jsnapy.jsnapy import SnapAdmin
