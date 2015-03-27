from setuptools import setup, find_packages

setup(name="jsnap-py",
      version="0.1",
      description="Python version of Junos Snapshot Administrator",
      author="Priyal Jain",
      author_email="jpriyal@juniper.net",
      license="Apache 2.0",
      keywords="Junos snapshot automation",
      url="http://www.github.com/Juniper/jsnap-py",
      package_dir={'': 'lib'},
      packages=find_packages('lib'), 
      package_data={
           'jnpr.jsnap.configs': ['*.yml'],
	       'jnpr.jsnap': ['content.html']
     },
      entry_points={
          'console_scripts': [
              'jsnap=jnpr.jsnap.jsnap:main',
          ],
      },
      zip_safe=False,
      install_requires=['junos-eznc', 'jinja2', 'colorama'],
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
