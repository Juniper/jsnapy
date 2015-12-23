import os
import yaml
import getpass
from jsnapy import SnapAdmin

js = SnapAdmin()
# making for single device

def extract_data(file_name, config_data):
    if os.path.isfile(config_data):
        print "insid if"
        data = open(config_data, 'r')
        config_data = yaml.load(data)
        print config_data
    elif type(config_data) is str:
        print "insid elif"
        config_data = yaml.load(config_data)
        print config_data
    else:
        print "incorrect config file or data, please chk !!!!"
        exit(-1)

    k = config_data.get('hosts')[0]
    hostname = k.get('devices')
    username = k.get('username') or raw_input("\n Enter user name: ")
    password = k.get('passwd') or getpass.getpass("\nPlease enter password to login to Device: ")
    snap_files = hostname + '_' + file_name
    return hostname,username,password, snap_files,config_data

def snap(file_name, data, dev= None):
    hostname, username, password, snap_file, config_data = extract_data(file_name, data)
    js.connect(hostname, username, password, config_data, snap_file, "snap")

def snapcheck(file_name, data, dev= None):
    print "\n inside snapcheck \n"
    hostname, username, password, snap_file, config_data = extract_data(file_name, data)
    result = js.connect(hostname, username, password, config_data, snap_file, "snapcheck")
    print "result for test case is:", result

def check(pre_file, post_file, data, dev= None):
    hostname, username, password, pre_snap, config_data = extract_data(pre_file, data)
    print "\n config_data: ", config_data
    post_snap = hostname + '_' + post_file
    print "connecting -----------"
    result = js.connect(hostname, username, password, config_data, pre_snap, "check", post_snap)
    print "\n result for test case is: ", result

