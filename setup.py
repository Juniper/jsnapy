#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

import os,sys
from setuptools import setup, find_packages
from setuptools.command.install import install
import ConfigParser

# dir_path = '/etc/jsnapy'
# dir_path = '/usr/local/share/jsnapy'
class OverrideInstall(install):
    # global dir_path
    # dire = None
    # user_options = install.user_options + [
    #         ('dire=', 'd', 'Location for snapshots and testfiles directories'),
    #     ] 
    # def initialize_options(self):
    #     install.initialize_options(self)
    #     self.dire = None
    #     # self.old_and_unmanageable = False
    #     # self.single_version_externally_managed = False
    # def finalize_options(self):
    #     install.finalize_options(self)
    #     dir_path = self.dire
    #     print dir_path
    def run(self):
        
        # print sys.argv
        # print self.install_data
        for arg in sys.argv:
            if '--install-data' in arg:
                break
        else:
            raise Exception("Must pass snapshot and testfile location in --install-data to setup.py")

            # raise Exception
            # dir_path = ''
            # while dir_path =='':
            #     dir_path= raw_input('Enter absolute directory path for testfiles and snapshots: ').strip()

            # self.install_data = dir_path 
            # # logging.error('Use --install-data to specify absolute directory path for snapshots and testfiles')
            # exit()
        dir_path = self.install_data
        mode = 0o777
        install.run(self)
        # self.extra_dirs
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
        config = ConfigParser.ConfigParser()
        config.set('DEFAULT','config_file_path','/etc/jsnapy')
        config.set('DEFAULT','snapshot_path',dir_path)
        config.set('DEFAULT','test_file_path',dir_path)

        with open("/etc/jsnapy/jsnapy.cfg",'w') as cfgfile:
            comment = ( '# This file can be overwritten\n'
                        '# It contains default path for\n'
                        '# config file, snapshots and testfiles\n'
                        '# If required, overwrite the path with your path\n'
                        '# config_file_path: path of main config file\n'
                        '# snapshot_path : path of snapshot file\n'
                        '# test_file_path: path of test file\n'
                        )
            cfgfile.write(comment)
            config.write(cfgfile)


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

setup(name="jsnapy",
      version=__version__,
      description="Python version of Junos Snapshot Administrator",
      author="Priyal Jain",
      author_email="jpriyal@juniper.net",
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
      data_files=[("", ['lib/jnpr/jsnapy/logging.yml']),
                  ('samples', example_files),
                  ('/etc/jsnapy', ['lib/jnpr/jsnapy/jsnapy.cfg']),
                  ('testfiles', ['testfiles/README']),
                  ('snapshots', ['snapshots/README']),
                  ('/var/log/jsnapy', log_files)
                 ],
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
