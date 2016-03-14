# jsnapy
Python version of Junos Snapshot Administrator

Inspired by https://github.com/Juniper/junos-snapshot-administrator

Abstract
========

  Junos Snapshot Administrator enables you to capture and audit runtime environment snapshots of your networked devices running   the Junos operating system (Junos OS).
  
  You can write your test cases in yaml file and run those tests cases against pre and post snapshots.
  
Installation
=============
Installation requires Python 2.7 and associated pip tool
      
    1. Install using pip command
          sudo pip install git+https://github.com/Juniper/jsnapy.git 
    2. Updating using pip command
          sudo pip install -U git+https://github.com/Juniper/jsnapy.git 
    3. Download or clone the source code from this git repository
          git clone https://github.com/Juniper/jsnapy
       Or Untar jsnapy-master.zip (if downloaded zip folder)
          unzip jsnapy-master.zip
       Go to jsnapy-master folder and install by:
          sudo python setup.py sdist
          sudo pip install dist/jsnap-py-0.1.tar.gz
          
Hello, World
=============
JSNAPy requires one main config file and test files.
Config file contains device details and test files to be executed.

config_check.yml:
```
# for one device, can be given like this:
    hosts:
      - devices: router 
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
3. jsnapy --check pre post -f config_check.yml
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

1. config file   
You can give either:
    - full file path  
    - only file name, it will first look in present working 
      directory, if file is not present then it will take file 
      path from "config_file_path" in jsnapy.cfg file. Default 
      onfig file path is "/etc/jsnapy"
2. test file: 
    - full file path  
    - only file name, in this case it will take path from "test_file_path" in jsnapy.cfg file. Default 
      onfig file path is "/etc/jsnapy/testfiles"
3. snap file:
    - full file path
    - prefix, in this case file name is formed automatically <(devicename_prefix_command/rpc.xml/text)>
      Snap files will be taken from "snapshot_path" in jsnapy.cfg file. 
      Default path is "/etc/jsnapy/snapshots"




          

