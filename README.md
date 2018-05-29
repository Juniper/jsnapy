[![PyPi Version](https://img.shields.io/pypi/v/jsnapy.svg)](https://pypi.python.org/pypi/jsnapy/) 
[![Coverage Status](https://travis-ci.org/Juniper/jsnapy.svg?branch=master)](https://travis-ci.org/Juniper/jsnapy)
[![Coverage Status](https://coveralls.io/repos/github/Juniper/jsnapy/badge.svg?branch=master)](https://coveralls.io/github/Juniper/jsnapy?branch=master)

# JSNAPy
Python version of Junos Snapshot Administrator

![JSNAPy logo](static/JSNAPy.png?raw=true "JSNAPy logo")

Inspired by https://github.com/Juniper/junos-snapshot-administrator

Abstract
========

  Junos Snapshot Administrator enables you to capture and audit runtime environment snapshots of your networked devices running   the Junos operating system (Junos OS).
  
  You can write your test cases in yaml file and run those tests cases against pre and post snapshots.
  
Installation
=============
Installation requires Python 2.7 and associated pip tool
      
    1. Install using pip command
          sudo pip install jsnapy
    2. Install using pip command from github
          sudo pip install git+https://github.com/Juniper/jsnapy.git 
    3. Updating using pip command (from github)
          sudo pip install -U git+https://github.com/Juniper/jsnapy.git 
    4. Download or clone the source code from this git repository
          git clone https://github.com/Juniper/jsnapy
       Or Untar jsnapy-master.zip (if downloaded zip folder)
          unzip jsnapy-master.zip
       Go to jsnapy-master folder and install by:
          sudo python setup.py sdist
          sudo pip install dist/jsnapy-x.x.tar.gz
          
Hello, World
=============
JSNAPy requires one main config file and test files.
Config file contains device details and test files to be executed.

config_check.yml:
```
# for one device, can be given like this:
    hosts:
      - device: router 
        username : abc
        passwd: pqr
    tests:
      - test_no_diff.yml 
```
test_no_diff.yml
```
test_command_version:
  - command: show interfaces terse lo* 
  - iterate:
      xpath: physical-interface
      id: './name'
      tests:
        - no-diff: oper-status       # element in which test is performed
          err: "Test Failed!! oper-status  got changed, before it was <{{pre['oper-status']}}>, now it is <{{post['oper-status']}}>"
          info: "Test Passed!! oper-status is same, before it is <{{pre['oper-status']}}> now it is <{{post['oper-status']}}> 
```

To run this test execute following command:
```
1. jsnapy --snap pre -f config_check.yml (for taking pre snapshot)
2. jsnapy --snap post -f config_check.yml (for taking post snapshot after some modification)
3. jsnapy --check pre post -f config_check.yml (compares pre post snapshot as per test cases)
4. jsnapy --diff pre post -f config_check.yml (compares pre post snapshot files, shows the diff in 2 Columns)
```

Output will look something like this:
```
(venv)sh-3.2# jsnapy --check pre post -f config_single_check.yml 
*************************Performing test on Device: 10.209.16.204*************************
Tests Included: test_command_version 
*************************Command is show interfaces terse lo**************************
----------------------Performing no-diff Test Operation----------------------
Test succeeded!! oper_status is same, before it is <['up']> now it is <['up']> 
Final result of no-diff: PASSED 
------------------------------- Final Result!! -------------------------------
Total No of tests passed: 1
Total No of tests failed: 0 
Overall Tests passed!!! 
```

File Paths:
--------------
```
1. config file   
   can give either:
    - full file path  
    - only file name, in this case JSNAPy will first look in present working 
      directory, if file is not present then it will take file path from "config_file_path" 
      in jsnapy.cfg file. Default config file path is "/etc/jsnapy"
2. test file: 
    - full file path  
    - only file name, in this case it will take path from "test_file_path" in jsnapy.cfg file. 
      Default test file path is "/etc/jsnapy/testfiles"
3. snap file:
    - full file path
    - tag, in this case file name is formed automatically (<devicename>_<tag>_<command/rpc>.<xml/text>)
      Snap files will be taken from "snapshot_path" in jsnapy.cfg file. 
      Default path is "/etc/jsnapy/snapshots"
```
jsnap2py: 
----------
Tool to convert conf file of JSNAP slax into yaml file that can be consumed by JSNAPy.
```
jsnap2py -i test_interface.conf
```
This will convert slax conf file "test_interface.conf" into yaml file "test_interface.yaml".  
If you want to give different output file name, then use -o option
```
jsnap2py -i test_interface.conf -o interface.yml
```
For more information please refer [jsnap2py-wiki] (https://github.com/Juniper/jsnapy/wiki/7.-jsnap2py)

CONTRIBUTORS
-------------

Juniper Networks is actively contributing to and maintaining this repo. Please contact jnpr-community-netdev@juniper.net for any queries.

Contributors:  

* v1.3.0: [Jasminderpal Singh Sidhu](https://github.com/sidhujasminder)
* v1.2.1: [Jasminderpal Singh Sidhu](https://github.com/sidhujasminder)
* v1.2.0: [Jasminderpal Singh Sidhu](https://github.com/sidhujasminder)
* v1.1.0: [Ishaan Kumar](https://github.com/eeishaan)
* v1.0.0: [Priyal Jain](https://github.com/jainpriyal), [Nitin Kumar](https://github.com/vnitinv)


