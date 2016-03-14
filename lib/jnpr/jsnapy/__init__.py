from .version import __version__
import ConfigParser
import os

class Singleton(object):
  _instance = None
  def __new__(cls, section, value, *args, **kwargs):
    if not isinstance(cls._instance, str):
        config = ConfigParser.ConfigParser({'config_file_path': '/etc/jsnapy', 'snapshot_path': '/etc/jsnapy/snapshots',
                                        'test_file_path': '/etc/jsnapy/testfiles', 'log_file_path': '/etc/logs/jsnapy'})
        config.read(os.path.join('/etc', 'jsnapy', 'jsnapy.cfg'))
        path = config.get(section, value)

        cls._instance = path
    return cls._instance

def get_path(section, value):
    return Singleton(section, value)

from jnpr.jsnapy.jsnapy import SnapAdmin
