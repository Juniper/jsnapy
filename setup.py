from setuptools import setup, find_packages

# parse requirements
req_lines = [line.strip() for line in open(
    'requirements.txt').readlines()]
install_reqs = list(filter(None, req_lines))

setup(name = "jsnap-py",
    version = "0.1",
    description = "Python version of Junos Snapshot Administrator",
    author = "Priyal Jain",
    author_email = "jpriyal@juniper.net",
    license="Apache 2.0",
    keywords="Junos snapshot automation",
    url="http://www.github.com/Juniper/jsnap-py",
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    package_data={
        'jsnap.configs': ['*.yml'],
    },
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
