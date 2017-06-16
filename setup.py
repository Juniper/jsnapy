#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import os
import sys
from os.path import expanduser
from setuptools import setup, find_packages
from setuptools.command.install import install
if sys.version < '3':
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser


class OverrideInstall(install):

    def run(self):

        for arg in sys.argv:
            if '--install-data' in arg:
                break
        else:
            #--------------------------------
            # hasattr(sys,'real_prefix') checks whether the
            # user is working in python virtual environment
            #--------------------------------
            if hasattr(sys, 'real_prefix'):
                self.install_data = os.path.join(sys.prefix, 'etc',
                                                 'jsnapy')
            elif 'win' in sys.platform:
                self.install_data = os.path.join(os.path.expanduser('~'),
                                                 'jsnapy')
            else:
                self.install_data = '/etc/jsnapy'

        dir_path = self.install_data
        mode = 0o777
        install.run(self)

        if 'win' not in sys.platform and not hasattr(sys, 'real_prefix'):
            os.chmod(dir_path, mode)
            for root, dirs, files in os.walk(dir_path):
                for directory in dirs:
                    os.chmod(os.path.join(root, directory), mode)
                for fname in files:
                    os.chmod(os.path.join(root, fname), mode)

            os.chmod('/var/log/jsnapy', mode)
            for root, dirs, files in os.walk('/var/log/jsnapy'):
                for directory in dirs:
                    os.chmod(os.path.join(root, directory), mode)
                for fname in files:
                    os.chmod(os.path.join(root, fname), mode)

        HOME = expanduser("~")  # correct cross platform way to do it
        home_folder = os.path.join(HOME, '.jsnapy')
        if not os.path.isdir(home_folder):
            os.mkdir(home_folder)
            os.chmod(home_folder, mode)

        if dir_path != '/etc/jsnapy':
            config = ConfigParser()
            config.set('DEFAULT','config_file_path',
                       dir_path)
            config.set('DEFAULT', 'snapshot_path',
                       os.path.join(dir_path, 'snapshots'))
            config.set('DEFAULT', 'test_file_path',
                       os.path.join(dir_path, 'testfiles'))

            if hasattr(sys, 'real_prefix'):
                default_config_location = os.path.join(sys.prefix,
                                                       'etc',
                                                       'jsnapy', 'jsnapy.cfg')
            elif 'win' in sys.platform:
                default_config_location = os.path.join(expanduser("~"),
                                                       'jsnapy', 'jsnapy.cfg')
            else:
                default_config_location = "/etc/jsnapy/jsnapy.cfg"

            if os.path.isfile(default_config_location):
                with open(default_config_location, 'w') as cfgfile:
                    comment = ('# This file can be overwritten\n'
                               '# It contains default path for\n'
                               '# config file, snapshots and testfiles\n'
                               '# If required, overwrite the path with'
                               '# your path\n'
                               '# config_file_path: path of main'
                               '# config file\n'
                               '# snapshot_path : path of snapshot file\n'
                               '# test_file_path: path of test file\n\n'
                               )
                    cfgfile.write(comment)
                    config.write(cfgfile)
            else:
                raise Exception('jsnapy.cfg not found at ' +
                                default_config_location)


req_lines = [line.strip() for line in open(
    'requirements.txt').readlines()]
install_reqs = list(filter(None, req_lines))
example_files = [
    os.path.join(
        'samples',
        i) for i in os.listdir('samples')]
log_files = [os.path.join('logs', j)
             for j in os.listdir('logs')]
exec(open('lib/jnpr/jsnapy/version.py').read())
os_data_file = []

if hasattr(sys, 'real_prefix'):
    home = os.path.join(sys.prefix, 'etc')
    os_data_file = [(os.path.join(home, 'jsnapy'),
                     ['lib/jnpr/jsnapy/logging.yml']),
                    (os.path.join(sys.prefix, 'var', 'logs', 'jsnapy'),
                     log_files),
                    ('samples', example_files),
                    (os.path.join(home, 'jsnapy'),
                     ['lib/jnpr/jsnapy/jsnapy.cfg']),
                    ('testfiles', ['testfiles/README']),
                    ('snapshots', ['snapshots/README'])
                    ]


elif 'win' in sys.platform:
    home = expanduser("~")
    os_data_file = [(os.path.join(home, 'jsnapy'),
                     ['lib/jnpr/jsnapy/logging.yml']),
                    (os.path.join(home, 'logs\jsnapy'), log_files),
                    ('samples', example_files),
                    (os.path.join(home, 'jsnapy'),
                     ['lib/jnpr/jsnapy/jsnapy.cfg']),
                    ('testfiles', ['testfiles/README']),
                    ('snapshots', ['snapshots/README'])
                    ]

else:
    os_data_file = [('/etc/jsnapy', ['lib/jnpr/jsnapy/logging.yml']),
                    ('samples', example_files),
                    ('/etc/jsnapy', ['lib/jnpr/jsnapy/jsnapy.cfg']),
                    ('testfiles', ['testfiles/README']),
                    ('snapshots', ['snapshots/README']),
                    ('/var/log/jsnapy', log_files)
                    ]

setup(name="jsnapy",
      version=__version__,
      description="Python version of Junos Snapshot Administrator",
      author="Priyal Jain",
      author_email="jnpr-community-netdev@juniper.net",
      license="Apache 2.0",
      keywords="Junos snapshot automation",
      url="http://www.github.com/Juniper/jsnapy",
      package_dir={'': 'lib'},
      packages=find_packages('lib'),
      package_data={
          'jnpr.jsnapy': ['jsnapy.cfg', 'logging.yml', 'content.html'],
      },
      entry_points={
          'console_scripts': [
              'jsnapy=jnpr.jsnapy.jsnapy:main',
          ],
      },
      scripts=['tools/jsnap2py'],
      zip_safe=False,
      install_requires=install_reqs,
      data_files=os_data_file,
      cmdclass={'install': OverrideInstall},
      classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: Text Processing :: Markup :: XML'
      ],
      )
