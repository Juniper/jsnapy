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
      
    1. Download or clone the source code from this git repository
          git clone https://github.com/Juniper/jsnapy
       Or Untar jsnapy-master.zip (if downloaded zip folder)
          unzip jsnapy-master.zip
    3. Go to jsnapy-master folder and install by:
          sudo python setup.py sdist
          sudo pip install dist/jsnap-py-0.1.tar.gz
          

