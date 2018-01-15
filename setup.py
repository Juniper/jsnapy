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
from six import iteritems


def set_logging_path(path):
    if os.path.exists(path):
        import yaml
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
                    elif 'win32' in sys.platform:
                        value['filename'] = (os.path.join
                                             (os.path.expanduser('~'),
                                              'logs\jsnapy\jsnapy.log'))

                with open(path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)


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
            elif 'win32' in sys.platform:
                self.install_data = os.path.join(os.path.expanduser('~'),
                                                 'jsnapy')
            else:
                self.install_data = '/etc/jsnapy'

        dir_path = self.install_data
        mode = 0o777
        install.run(self)

        if 'win32' not in sys.platform and not hasattr(sys, 'real_prefix'):
            dir_mode = 0o755
            file_mode = 0o644
            os.chmod(dir_path, dir_mode)
            for root, dirs, files in os.walk(dir_path):
                for fname in files:
                    os.chmod(os.path.join(root, fname), file_mode)

            os.chmod('/var/log/jsnapy', mode)
            for root, dirs, files in os.walk('/var/log/jsnapy'):
                for directory in dirs:
                    os.chmod(os.path.join(root, directory), mode)
                for fname in files:
                    os.chmod(os.path.join(root, fname), mode)

        # mode = 0o755
        # HOME = expanduser("~")  # correct cross platform way to do it
        # home_folder = os.path.join(HOME, '.jsnapy')
        # if not os.path.isdir(home_folder):
        #     os.mkdir(home_folder)
        #     os.chmod(home_folder, mode)

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
            elif 'win32' in sys.platform:
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

            if hasattr(sys, 'real_prefix'):
                path = os.path.join(sys.prefix, 'etc', 'jsnapy', 'logging.yml')
                set_logging_path(path)
            elif 'win32' in sys.platform:
                path = os.path.join(expanduser("~"), 'jsnapy', 'logging.yml')
                set_logging_path(path)



req_lines = [line.strip() for line in open(
    'requirements.txt').readlines()]
install_reqs = list(filter(None, req_lines))
log_files = [os.path.join('logs', j)
             for j in os.listdir('logs')]
exec(open('lib/jnpr/jsnapy/version.py').read())
os_data_file = []

#----------------------------
# In os_data_file variable,
# the self.install_data path is taken as default prefix to
# the new created directories and files.
# Specifying the '.' means the directory directly specified
# by self.install_data path.
# Specifying only 'samples' means 'install_data Path'/samples
#----------------------------

if hasattr(sys, 'real_prefix'):
    os_data_file = [('.', ['lib/jnpr/jsnapy/logging.yml']),
                    ('../../var/logs/jsnapy', log_files),
                    ('.', ['lib/jnpr/jsnapy/jsnapy.cfg']),
                    ('testfiles', ['testfiles/README']),
                    ('snapshots', ['snapshots/README'])
                    ]

elif 'win32' in sys.platform:
    os_data_file = [('.', ['lib/jnpr/jsnapy/logging.yml']),
                    ('../logs/jsnapy', log_files),
                    ('.', ['lib/jnpr/jsnapy/jsnapy.cfg']),
                    ('testfiles', ['testfiles/README']),
                    ('snapshots', ['snapshots/README'])
                    ]

else:
    os_data_file = [('/etc/jsnapy', ['lib/jnpr/jsnapy/logging.yml']),
                    ('/etc/jsnapy', ['lib/jnpr/jsnapy/jsnapy.cfg']),
                    ('/var/log/jsnapy', log_files)
                    ]

setup(name="jsnapy",
      version=__version__,
      description="Python version of Junos Snapshot Administrator",
      author="Priyal Jain, Nitin Kumar",
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
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: Text Processing :: Markup :: XML'
      ],
      )
