from setuptools import setup, find_packages
import os

req_lines = [line.strip() for line in open(
    'requirements.txt').readlines()]
install_reqs = list(filter(None, req_lines))
example_files = [os.path.join('lib/jnpr/jsnapy/samples',i) for i in os.listdir('lib/jnpr/jsnapy/samples')]
log_files = [os.path.join('lib/jnpr/jsnapy/logs',j) for j in os.listdir('lib/jnpr/jsnapy/logs')]
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
           'jnpr.jsnapy.samples': ['*.yml'],
           'jnpr.jsnapy': ['jsnapy.cfg','hosts.yml', 'logging.yml', 'content.html'],
           'jnpr.jsnapy.snapshots': ['README'],
           'jnpr.jsnapy.testfiles': ['README'],
           'jnpr.jsnapy.logs': ['*.log']
     },
      entry_points={
          'console_scripts': [
              'jsnapy=jnpr.jsnapy.jsnapy:main',
          ],
      },
      zip_safe=False,
      install_requires= install_reqs,
      data_files=[('/etc/jsnapy', ['lib/jnpr/jsnapy/logging.yml']),
                  ('/etc/jsnapy/samples', example_files),
                  ('/etc/jsnapy', ['lib/jnpr/jsnapy/jsnapy.cfg']),
                  ('/etc/jsnapy', ['lib/jnpr/jsnapy/hosts.yml']),
                  ('/etc/jsnapy/testfiles', ['lib/jnpr/jsnapy/testfiles/README']),
                  ('/etc/jsnapy/snapshots', ['lib/jnpr/jsnapy/snapshots/README']),
                  ('/etc/logs/jsnapy', log_files)
                  ],
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
