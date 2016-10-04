# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

from .version import __version__
import ConfigParser
import os
import colorama
colorama.init(autoreset=True)

class DirStore:
    custom_dir = None
        
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
    custom_dir = DirStore.custom_dir
    if custom_dir:
        paths = {'config_file_path': '',
                'snapshot_path': 'snapshots',
                'test_file_path': 'testfiles'}
        if custom_dir.startswith('~/'):
            custom_dir = os.path.join(os.path.expanduser('~'),custom_dir[2:])
        complete_paths = {}
        for p in paths:
            complete_paths[p]= os.path.join(custom_dir,paths[p])
        path = complete_paths.get(value)
    else:    
        config = ConfigParser.ConfigParser()
        config_location = get_config_location()
        if config_location is None:
            raise Exception('Config file not found')
        config_location = os.path.join(config_location,'jsnapy.cfg')
        config.read(config_location)
        path = config.get(section, value)
    return path

from jnpr.jsnapy.jsnapy import SnapAdmin