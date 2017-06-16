#!/usr/bin/python

# Copyright (c) 1999-2016, Juniper Networks Inc.
#
# All rights reserved.
#

from six import iteritems
import argparse
import getpass
import logging
import os
import queue
import sys
import textwrap
from copy import deepcopy
from threading import Thread

import yaml
from jnpr.jsnapy import get_path, version, get_config_location, DirStore
from jnpr.jsnapy.check import Comparator
from jnpr.jsnapy.notify import Notification
from jnpr.junos import Device
from jnpr.jsnapy import version
from jnpr.jsnapy.operator import Operator
from jnpr.jsnapy.snap import Parser
from jnpr.junos.exception import ConnectAuthError

import colorama
from . import setup_logging


logging.getLogger("paramiko").setLevel(logging.WARNING)

class SnapAdmin:

    # need to call this function to initialize logging
    setup_logging.setup_logging()

    def __init__(self):
        """
        taking parameters from command line
        """
        self.q = queue.Queue()
        self.snap_q = queue.Queue()
        self.log_detail = {'hostname': None}
        self.snap_del = False
        self.logger = logging.getLogger(__name__)
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description=textwrap.dedent('''\
                                        Tool to capture snapshots and compare them
                                        It supports four subcommands:
                                         --snap, --check, --snapcheck, --diff
                                        1. Take snapshot:
                                                jsnapy --snap pre_snapfile -f main_configfile
                                        2. Compare snapshots:
                                                jsnapy --check post_snapfile pre_snapfile -f main_configfile
                                        3. Compare current configuration:
                                                jsnapy --snapcheck snapfile -f main_configfile
                                        4. Take diff without specifying test case:
                                                jsnapy --diff pre_snapfile post_snapfile -f main_configfile
                                            '''),
            usage="\nThis tool enables you to capture and audit runtime environment of "
            "\nnetworked devices running the Junos operating system (Junos OS)\n")

        group = self.parser.add_mutually_exclusive_group()
        # for mutually exclusive gp, can not use two or more options at a time
        group.add_argument(
            '--snap',
            action='store_true',
            help="take the snapshot for commands specified in test file")
        group.add_argument(
            '--check',
            action='store_true',
            help=" compare pre and post snapshots based on test operators specified in test file")
        
        group.add_argument(
            '--snapcheck',
            action='store_true',
            help='check current snapshot based on test file')
        
      #########
      # will supoort it later
      # for windows
      ########
      #  group.add_argument(
      #      "--init",
      #      action="store_true",
      #      help="generate init folders: snapshots, configs and main.yml",
      #  )
      #########

        group.add_argument(
            "--diff",
            action="store_true",
            help="display difference between two snapshots"
        )
        group.add_argument(
            "-V", "--version",
            action="store_true",
            help="displays version"
        )

        self.parser.add_argument(
            "pre_snapfile",
            nargs='?',
            help="pre snapshot filename")       # make it optional
        self.parser.add_argument(
            "post_snapfile",
            nargs='?',
            help="post snapshot filename",
            type=str)       # make it optional
        self.parser.add_argument(
            "-T", "--testfiles",
            nargs="+",
            help="test file paths")  # Take test file/files as an argument 
        self.parser.add_argument(
            "-f", "--file",
            help="config file to take snapshot",
            type=str)
        self.parser.add_argument(
            "--local",
            action="store_true",
            help="whether to run snapcheck on local snapshot")
        self.parser.add_argument(
            "--folder",
            help="custom directory path for lookup",
            type=str)
        self.parser.add_argument("-t", "--hostname", help="hostname", type=str)
        self.parser.add_argument(
            "-p",
            "--passwd",
            help="password to login",
            type=str)
        self.parser.add_argument(
            "-l",
            "--login",
            help="username to login",
            type=str)
        self.parser.add_argument(
            "-P",
            "--port",
            help="port no to connect to device",
            type=int
        )
        self.parser.add_argument(
            "-v", "--verbosity",
            action = "count",
            help= textwrap.dedent('''\
            Set verbosity
            -v: Debug level messages
            -vv: Info level messages
            -vvv: Warning level messages
            -vvvv: Error level messages
            -vvvvv: Critical level messages''')
        )
       # self.parser.add_argument(
       #     "-m",
       #     "--mail",
       #     help="mail result to given id",
       #     type=str)
        # self.parser.add_argument(
        #    "-o",
        #    "--overwrite",
        #    action='store_true',
        #    help="overwrite directories and files generated by init",
        #)

        #self.args = self.parser.parse_args()
        self.args, unknown = self.parser.parse_known_args()

        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""
        self.db['first_snap_id'] = None
        self.db['second_snap_id'] = None
        
        DirStore.custom_dir=self.args.folder

    def get_version(self):
        """
        This function gives version of Jsnapy
        :return: return JSNAPy version
        """
        return version.__version__

    '''
    def generate_init(self):
       """
       # generate init folder, will support it later
        create snapshots and configs folder along with sample main config file.
        All snapshots generated will go in snapshots folder. configs folder will contain
        all the yaml file apart from main, like device.yml, bgp_neighbor.yml
        :return:
       """

        mssg = "Creating Jsnapy directory structure at: ", os.getcwd()
        self.logger.debug(colorama.Fore.BLUE + mssg)
        if not os.path.isdir("snapshots"):
            os.mkdir("snapshots")
        dst_config_path = os.path.join(os.getcwd(), 'configs')
         overwrite files if given option -o or --overwrite
        if not os.path.isdir(dst_config_path) or self.args.overwrite is True:
            distutils.dir_util.copy_tree(os.path.join(os.path.dirname(__file__), 'configs'),
                                         dst_config_path)
        dst_main_yml = os.path.join(dst_config_path, 'main.yml')
        if not os.path.isfile(
                os.path.join(os.getcwd(), 'main.yml')) or self.args.overwrite is True:
            shutil.copy(dst_main_yml, os.getcwd())

        logging_yml_file = os.path.join(
            os.path.dirname(__file__),
            'logging.yml')
        if not os.path.isfile(
                os.path.join(os.getcwd(), 'logging.yml')) or self.args.overwrite is True:
            shutil.copy(logging_yml_file, os.getcwd())
        mssg1= "Successfully created Jsnap directories at:",os.getcwd()
        self.logger.info(colorama.Fore.BLUE + mssg1)
    '''

    def set_verbosity(self, val):
        self.logger.root.setLevel(val)
        handlers = self.logger.root.handlers
        for handle in handlers:
            if handle.__class__.__name__=='StreamHandler':
                handle.setLevel(val)

    def chk_database(self, config_file, pre_snapfile,
                     post_snapfile, check=None, snap=None, action=None):
        """
        This function test parameters for sqlite and then update database accordingly
        :param config_file: main config file
        :param pre_snapfile: pre snapshot file
        :param post_snapfile: post snapshot file
        :param check: True if --check operator is given
        :param snap:
        :param action: used by module version, either snap, check or snapcheck
        """
        d = config_file['sqlite'][0]
        compare_from_id = False
        if d.__contains__('store_in_sqlite'):
            self.db['store_in_sqlite'] = d['store_in_sqlite']
        if d.__contains__('check_from_sqlite'):
            self.db['check_from_sqlite'] = d['check_from_sqlite']

        if (self.db['store_in_sqlite']) or (self.db['check_from_sqlite']):
                                            # and (check is True or action is
                                            # "check")):
            if d.__contains__('database_name'):
                self.db['db_name'] = d['database_name']

            else:
                self.logger.error(
                    colorama.Fore.RED +
                    "Specify name of the database.",
                    extra=self.log_detail)
                exit(1)
            if check is True or self.args.diff is True or action is "check":
                if 'compare' in list(d) and d['compare'] is not None:
                    strr = d['compare']
                    if not isinstance(strr, str):
                        self.logger.error(colorama.Fore.RED + "Properly specify ids of first and "
                                                              "second snapshot in format: first_snapshot_id, second_snapshot_id", extra=self.log_detail)
                        exit(1)
                    compare_from_id = True
                    lst = [val.strip() for val in strr.split(',')]
                    try:
                        lst = [int(x) for x in lst]
                    except ValueError as ex:
                        self.logger.error(colorama.Fore.RED + "Properly specify id numbers of first and second snapshots"
                                          " in format: first_snapshot_id, second_snapshot_id", extra=self.log_detail)
                        #raise Exception(ex)
                        exit(1)
                    if len(lst) > 2:
                        self.logger.error(colorama.Fore.RED + "No. of snapshots specified is more than two."
                                          " Please specify only two snapshots.", extra=self.log_detail)
                        exit(1)
                    if len(lst) == 2 and isinstance(
                            lst[0], int) and isinstance(lst[1], int):
                        self.db['first_snap_id'] = lst[0]
                        self.db['second_snap_id'] = lst[1]
                    else:
                        self.logger.error(colorama.Fore.RED + "Properly specify id numbers of first and second snapshots"
                                          " in format: first_snapshot_id, second_snapshot_id", extra=self.log_detail)
                        exit(1)
        if self.db['check_from_sqlite'] is False or compare_from_id is False:
            if (check is True and (pre_snapfile is None or post_snapfile is None) or
                    self.args.diff is True and (pre_snapfile is None or post_snapfile is None)):
                self.logger.error(
                    colorama.Fore.RED +
                    "Arguments not given correctly, Please refer below help message", extra=self.log_detail)
                self.parser.print_help()
                sys.exit(1)

    def get_hosts(self):
        """
        Called by main function, it extracts main config file and also check for database
        Reads the yaml config file given by user and pass the extracted data to login function to
        read device details and connect them. Also checks sqlite key to check if user wants to
        create database for snapshots
        """
        self.logger.debug(colorama.Fore.BLUE +
                "jsnapy.cfg file location used : %s" %
                get_config_location(), extra=self.log_detail)
        self.logger.debug(colorama.Fore.BLUE +
                "Configuration file location used : %s" %
                get_path('DEFAULT', 'config_file_path'), extra=self.log_detail)
                        
        if self.args.pre_snapfile is not None:
            output_file = self.args.pre_snapfile
        elif self.args.snapcheck is True and self.args.pre_snapfile is None:
            output_file = "snap_temp"
            self.snap_del = True
        else:
            output_file = ""
        conf_file = self.args.file
        check = self.args.check
        snap = self.args.snap
        if conf_file is not None:
            if os.path.isfile(conf_file):
                config_file = open(conf_file, 'r')
                self.main_file = yaml.load(config_file)
            elif os.path.isfile(os.path.join(get_path('DEFAULT', 'config_file_path'), conf_file)):
                fpath = get_path('DEFAULT', 'config_file_path')
                config_file = open(os.path.join(fpath, conf_file), 'r')
                self.main_file = yaml.load(config_file)
            else:
                self.logger.error(
                    colorama.Fore.RED +
                    "ERROR!! Config file '%s' is not present " %
                    conf_file, extra=self.log_detail)
                sys.exit(1)
        else:
            if self.args.hostname and self.args.testfiles:
                temp_dict = {'hosts':[{'device':'', 'username':'', 'passwd':''}], 'tests':[]}
                temp_dict['hosts'][0]['device'] = self.args.hostname
                temp_dict['hosts'][0]['username'] = self.args.login
                temp_dict['hosts'][0]['passwd'] = self.args.passwd
                for tfile in self.args.testfiles:
                    temp_dict['tests'].append(tfile)
                self.main_file = temp_dict


        #### if --check option is given for sqlite, then snap file name is not compulsory  ####
        #### else exit the function saying arguments not correct  ####
        if self.main_file.__contains__(
                'sqlite') and self.main_file['sqlite'] and self.main_file['sqlite'][0]:
            self.chk_database(
                self.main_file,
                self.args.pre_snapfile,
                self.args.post_snapfile,
                check,
                snap)
        else:
            if (self.args.check is True and (
                    self.args.file is None or self.args.pre_snapfile is None or self.args.post_snapfile is None)):
                self.logger.error(colorama.Fore.RED +
                                  "Arguments not given correctly, Please refer help message",
                                  extra=self.log_detail)
                self.parser.print_help()
                sys.exit(1)
        self.login(output_file)

    def generate_rpc_reply(self, dev, output_file, hostname, config_data):
        """
        Generates rpc-reply based on command/rpc given and stores them in snap_files
        :param dev: device handler
        :param output_file: filename to store snapshots
        :param hostname: hostname of device
        :param config_data : data of main config file
        """
        val = None
        test_files = []
        for tfile in config_data.get('tests'):
            if not os.path.isfile(tfile):
                tfile = os.path.join(
                    get_path(
                        'DEFAULT',
                        'test_file_path'),
                    tfile)
            if os.path.isfile(tfile):
                test_file = open(tfile, 'r')
                test_files.append(yaml.load(test_file))
            else:
                self.logger.error(
                    colorama.Fore.RED +
                    "ERROR!! File %s is not found for taking snapshots" %
                    tfile, extra=self.log_detail)

        g = Parser()
        for tests in test_files:
            val = g.generate_reply(tests, dev, output_file, hostname, self.db)
        return val

    def compare_tests(
            self, hostname, config_data, pre_snap=None, post_snap=None, action=None):
        """
        called by check and snapcheck argument, to compare snap files
        calls the function to compare snapshots based on arguments given
        (--check, --snapcheck, --diff)
        :param hostname: device name
        :return: return object of Operator containing test details
        """
        comp = Comparator()
        chk = self.args.check
        diff = self.args.diff
        pre_snap_file = self.args.pre_snapfile if pre_snap is None else pre_snap
        if (chk or diff or action in ["check", "diff"]):
            post_snap_file = self.args.post_snapfile if post_snap is None else post_snap
            test_obj = comp.generate_test_files(
                config_data,
                hostname,
                chk,
                diff,
                self.db,
                self.snap_del,
                pre_snap_file,
                action,
                post_snap_file)
        else:
            test_obj = comp.generate_test_files(
                config_data,
                hostname,
                chk,
                diff,
                self.db,
                self.snap_del,
                pre_snap_file,
                action)
        return test_obj

    def get_values(self, key_value):
        del_value = ['device', 'username', 'passwd' ]
        for v in del_value:
            if v in list(key_value):
                del key_value[v]
        return key_value


    def login(self, output_file):
        """
        Extract device information from main config file. Stores device information and call connect function,
        device can be single or multiple. Instead of connecting to all devices mentioned in yaml file, user can
        connect to some particular group of device also.
        :param output_file: name of snapshot file
        """
        self.host_list = []
        if self.args.hostname is None:
            host_dict={}
            try:
                hosts_val = self.main_file['hosts']
            except KeyError as ex:
                self.logger.error(colorama.Fore.RED +
                "\nERROR occurred !! Hostname not given properly %s" %
                str(ex),
                extra=self.log_detail)
                #raise Exception(ex)
            except Exception as ex:
                self.logger.error(colorama.Fore.RED +
                "\nERROR occurred !! %s" %
                str(ex),
                extra=self.log_detail)
                #raise Exception(ex)
            else:
                # when group of devices are given, searching for include keyword in
                # hosts in main.yaml file
                first_entry = hosts_val[0]
                if 'include' in first_entry:
                    devices_file_name = first_entry['include']
                    if os.path.isfile(devices_file_name):
                        lfile = devices_file_name
                    else:
                        lfile = os.path.join(
                                    get_path(
                                        'DEFAULT',
                                        'test_file_path'),
                                    devices_file_name)
                    login_file = open(lfile, 'r')
                    dev_file = yaml.load(login_file)
                    gp = first_entry.get('group', 'all')

                    dgroup = [i.strip().lower() for i in gp.split(',')]
                    for dgp in dev_file:
                        if dgroup[0].lower() == 'all' or dgp.lower() in dgroup:
                            for val in dev_file[dgp]:
                                hostname = list(val)[0]
                                self.log_detail = {'hostname': hostname}
                                if val.get(hostname) is not None and hostname not in host_dict:
                                    host_dict[hostname] = deepcopy(val.get(hostname))
                                    self.host_list.append(hostname)
                # login credentials are given in main config file, can connect to multiple devices
                else:
                    #key_value = deepcopy(k)
                    for host in hosts_val:
                        try:
                            hostname = host['device']
                            self.log_detail = {'hostname': hostname}
                        except KeyError as ex:
                            self.logger.error(
                            colorama.Fore.RED +
                            "ERROR!! KeyError 'device' key not found",
                            extra=self.log_detail)
                            #raise Exception(ex)
                        except Exception as ex:
                            self.logger.error(
                            colorama.Fore.RED +
                            "ERROR!! %s" %
                            ex,
                            extra=self.log_detail)
                            #raise Exception(ex)
                        else:
                            if hostname not in host_dict:
                                self.host_list.append(hostname)
                                # host.pop('device')
                                host_dict[hostname] = deepcopy(host)

            for (hostname, key_value) in iteritems(host_dict):
                #The file config takes precedence over cmd line params -- no changes made
                username = self.args.login or key_value.get('username') 
                password = self.args.passwd or key_value.get('passwd') 
                #if --port arg is given on the cmd then that takes precedence                
                port = self.args.port
                if port is not None:
                    key_value['port'] = port
                key_value = self.get_values(key_value)
                t = Thread(
                    target=self.connect,
                    args=(
                        hostname,
                        username,
                        password,
                        output_file
                    ),
                    kwargs= key_value
                )
                t.start()
                t.join()
        # login credentials are given from command line
        else:
            hostname = self.args.hostname
            self.log_detail = {'hostname': hostname}
            username = self.args.login
            password = self.args.passwd
            # if self.args.passwd is not None else getpass.getpass("\nEnter
            # Password: ")
            self.host_list.append(hostname)
            port = self.args.port
            key_value = {'port': port} if port is not None else {}
            self.connect(hostname, username, password, output_file, **key_value)

    def get_test(self, config_data, hostname, snap_file, post_snap, action):
        """
        Analyse testfile and return object of operator.Operator containing test details
        called by connect() function and other functions of Jsnapy module functions
        :param config_data: data of main config file
        :param hostname: hostname
        :param snap_file: pre snapshot file name
        :param post_snap: post snapshot file name
        :param action: action to be taken (check, snapcheck, snap)
        :return: object of testop.Operator containing test details
        """
        res = Operator()

        res = self.compare_tests(
                hostname,
                config_data,
                snap_file,
                post_snap,
                action)

        result_status = res.result
        
        mail_condition = 'all'
        if result_status == 'Passed':
            mail_condition = 'pass'
        elif result_status == 'Failed':
            mail_condition = 'fail'

        mail_pref =  config_data.get("mail") 

        #we don't want to send mail when diff operation is run
        if  mail_pref is not None and self.args.diff is False:
            mail_file_path = None
            if type(mail_pref) is str:
                mail_file_path = mail_pref
            elif type(mail_pref) is dict: 
                if mail_condition in mail_pref:
                    mail_file_path = mail_pref.get(mail_condition)
            else:
                self.logger.error(
                    colorama.Fore.RED +
                    "ERROR!! Type of mail preferences should be either dictionary or string", extra=self.log_detail)
                    
            if mail_file_path is not None and mail_file_path != '' :
                mfile = os.path.join(get_path('DEFAULT', 'test_file_path'), mail_file_path)\
                        if os.path.isfile(mail_file_path) is False else mail_file_path
                if os.path.isfile(mfile):
                    mail_file = open(mfile, 'r')
                    mail_file = yaml.load(mail_file)
                    if "passwd" not in mail_file:
                        passwd = getpass.getpass(
                            "Please enter ur email password ")
                    else:
                        passwd = mail_file['passwd']
                
                    send_mail = Notification()
                    send_mail.notify(mail_file, hostname, passwd, res)
                else:
                    self.logger.error(
                        colorama.Fore.RED +
                        "ERROR!! Path of file containing mail content is not correct", extra=self.log_detail)
        # else:
        #     res = self.compare_tests(
        #         hostname,
        #         config_data,
        #         snap_file,
        #         post_snap,
        #         action)

        self.q.put(res)
        return res

    def connect(self, hostname, username, password, output_file,
                config_data=None, action=None, post_snap=None, **kwargs):
        """
        connect to device and calls the function either to generate snapshots
        or compare them based on option given (--snap, --check, --snapcheck, --diff)
        :param hostname: ip/ hostname of device
        :param username: username of device
        :param password: password to connect to device
        :param snap_files: file name to store snapshot
        :return: if snap operation is performed then return true on success
                 if snapcheck or check operation is performed then return test details
        """
        res = None
        if config_data is None:
            config_data = self.main_file

        if 'local' in config_data:
            self.args.local = True
        
        if (self.args.snap is True or action is "snap") or ( (self.args.snapcheck is True or action is "snapcheck") and self.args.local is not True ):
            self.logger.info(
                colorama.Fore.BLUE +
                "Connecting to device %s ................", hostname, extra=self.log_detail)
            if username is None:
                if username is None:
                    if sys.version < '3':
                        username = raw_input("\nEnter User name: ")
                    else:
                        username = input("\nEnter User name: ")
            dev = Device(
                host=hostname,
                user=username,
                passwd=password,
                gather_facts=False,
                **kwargs)
            try:
                dev.open()
            except ConnectAuthError as ex:
                if password is None and action is None:
                    password = getpass.getpass(
                        "\nEnter Password for username <%s> : " %
                        username)
                    self.connect(
                        hostname,
                        username,
                        password,
                        output_file,
                        config_data,
                        action,
                        post_snap,
                        **kwargs)
                else:
                    self.logger.error(colorama.Fore.RED +
                                      "\nERROR occurred %s" %
                                      str(ex),
                                      extra=self.log_detail)
                    raise Exception(ex)
            except Exception as ex:
                self.logger.error(colorama.Fore.RED +
                                  "\nERROR occurred %s" %
                                  str(ex),
                                  extra=self.log_detail)
                raise Exception(ex)
            else:
                res = self.generate_rpc_reply(
                    dev,
                    output_file,
                    hostname,
                    config_data)
                self.snap_q.put(res)
                dev.close()
        if self.args.check is True or self.args.snapcheck is True or self.args.diff is True or action in [
                "check", "snapcheck"]:
            
            
            if self.args.local is True and 'local' in config_data:
                output_file = config_data['local']
                res = {}
                for local_snap in output_file:
                    ret_obj = self.get_test(
                                config_data,
                                hostname,
                                local_snap,
                                post_snap,
                                action)
                    res[local_snap] = ret_obj
            else:
                res = self.get_test(
                            config_data,
                            hostname,
                            output_file,
                            post_snap,
                            action)     
                
        return res

    ############################### functions to support module ##############

    def multiple_device_details(
            self, hosts, config_data, pre_name, action, post_name):
        """
        Called when multiple devices are given in config file
        :param hosts: List of devices or a includes a file
        :param config_data: data of main config file
        :param pre_name: pre snapshot filename or file tag
        :param action: action to be taken, snap, snapcheck, check
        :param post_name: post snapshot filename or file tag
        :return: return object of testop.Operator containing test details
        """
        res_obj = []
        self.host_list = []
        host_dict={}

        first_entry = hosts[0]
        if 'include' in first_entry:
            devices_file_name = first_entry['include']
            if os.path.isfile(devices_file_name):
                lfile = devices_file_name
            else:
                lfile = os.path.join(
                            get_path(
                                'DEFAULT',
                                'test_file_path'),
                            devices_file_name)
            login_file = open(lfile, 'r')
            dev_file = yaml.load(login_file)
            gp = first_entry.get('group', 'all')

            dgroup = [i.strip().lower() for i in gp.split(',')]
            for dgp in dev_file:
                if dgroup[0].lower() == 'all' or dgp.lower() in dgroup:
                    for val in dev_file[dgp]:
                        hostname = list(val)[0]
                        self.log_detail = {'hostname': hostname}
                        if val.get(hostname) is not None and hostname not in host_dict:
                            host_dict[hostname] = deepcopy(val.get(hostname))
                            self.host_list.append(hostname)
        else:
            for host in hosts:
                try:
                    hostname = host['device']
                    self.log_detail = {'hostname': hostname}
                except KeyError as ex:
                    self.logger.error(
                    colorama.Fore.RED +
                    "ERROR!! KeyError 'device' key not found",
                    extra=self.log_detail)
                except Exception as ex:
                    self.logger.error(
                    colorama.Fore.RED +
                    "ERROR!! %s" %
                    ex,
                    extra=self.log_detail)
                else:
                    if hostname not in host_dict:
                        self.host_list.append(hostname)
                        host_dict[hostname] = deepcopy(host)

        for (hostname, key_value) in iteritems(host_dict):
            username = key_value.get('username')
            password = key_value.get('passwd')
            key_value = self.get_values(key_value)
            t = Thread(
                target=self.connect,
                args=(
                    hostname,
                    username,
                    password,
                    pre_name,
                    config_data,
                    action,
                    post_name),
                kwargs= key_value
            )
            t.start()
            t.join()
            if action == "snap":
                if not self.snap_q.empty():
                    res_obj.append(self.snap_q.get())
            elif action in ["snapcheck", "check"]:
                if not self.q.empty():
                    res_obj.append(self.q.get())
            else:
                res_obj.append(None)

        return res_obj

    def extract_data(
            self, config_data, pre_name=None, action=None, post_name=None, local=False):
        """
        Called when dev= None, i.e. device details are passed inside config file
        It parse details of main config file and call functions to connect to device
        and take snapshots
        :param config_data: data of main config file
        :param pre_name: pre snapshot filename or file tag
        :param action: action to be taken, snap, snapcheck, check
        :param post_name: post snapshot filename or file tag
        :param local: reuse exisiting snapshot when true. Defaults to False        
        :return: return list of object of testop.Operator containing test details or list of dictionary of object of testop.Operator containing test details for each stored snapshot
        """
        val =[]
        if os.path.isfile(config_data):
            data = open(config_data, 'r')
            config_data = yaml.load(data)
        elif isinstance(config_data, str):
            config_data = yaml.load(config_data)
        else:
            self.logger.info(
                colorama.Fore.RED +
                "Incorrect config file or data, please chk !!!!", extra=self.log_detail)
            exit(1)
        try:
            host = config_data.get('hosts')[0]
        except Exception as ex:
            self.logger.error(
                colorama.Fore.RED +
                "ERROR!! config file %s is not present" %
                ex,
                extra=self.log_detail)
            raise Exception("config file is not present ", ex)
        else:
            self.args.local = local
            if config_data.__contains__(
                    'sqlite') and config_data['sqlite'] and config_data['sqlite'][0]:
                self.chk_database(
                    config_data,
                    pre_name,
                    post_name,
                    None,
                    None,
                    action)
            if host.__contains__('include') or len(config_data.get('hosts'))>1:
                res_obj = self.multiple_device_details(
                    config_data.get('hosts'),
                    config_data,
                    pre_name,
                    action,
                    post_name)
                return res_obj
            else:
                hostname = host.get('device')
                self.log_detail = {'hostname': hostname}
                username = host.get('username')
                password = host.get('passwd')
                key_value = host
                key_value= self.get_values(key_value)
                #pre_name = hostname + '_' + pre_name if not os.path.isfile(pre_name) else pre_name
                # if action is "check":
                #    post_name= hostname + '_' + post_name if not os.path.isfile(post_name) else post_name
                val.append(self.connect(
                    hostname,
                    username,
                    password,
                    pre_name,
                    config_data,
                    action,
                    post_name,
                    **key_value))
                return val

    def extract_dev_data(
            self, dev, config_data, pre_name=None, action=None, post_snap=None, local=False):
        """
        Used to parse details given in main config file, when device object is passed in function
        :param dev: Device object
        :param config_data: data of main config file
        :param pre_name: pre snapshot filename or file tag
        :param action: action to be taken, snap, check or snapcheck
        :param post_snap: post snapshot filename or file tag
        :param local: reuse exisiting snapshot when true. Defaults to False
        :return: return list of object of testop.Operator containing test details or list of dictionary of object of testop.Operator containing test details for each stored snapshot
        """
        res = []
        if isinstance(config_data, dict):
            pass
        elif os.path.isfile(config_data):
            data = open(config_data, 'r')
            config_data = yaml.load(data)
        elif isinstance(config_data, str):
            config_data = yaml.load(config_data)
        else:
            self.logger.info(
                colorama.Fore.RED +
                "Incorrect config file or data, please chk !!!!", extra=self.log_detail)
            exit(1)
        try:
            hostname = dev.hostname
            self.log_detail = {'hostname': hostname}
        except Exception as ex:
            self.logger.error(
                colorama.Fore.RED +
                "ERROR!! message is: %s" %
                ex,
                extra=self.log_detail)
            raise Exception(ex)
        else:
            if config_data.__contains__(
                    'sqlite') and config_data['sqlite'] and config_data['sqlite'][0]:
                self.chk_database(
                    config_data,
                    pre_name,
                    post_snap,
                    None,
                    None,
                    action)
            
            
            if 'local' in config_data:
                local = True 

            if action is "snap" or ( action is "snapcheck" and local is False ) :
                try:
                    res.append(self.generate_rpc_reply(
                        dev,
                        pre_name,
                        hostname,
                        config_data))
                except Exception as ex:
                    self.logger.error(colorama.Fore.RED +
                                      "\nERROR occurred %s" %
                                      str(ex),
                                      extra=self.log_detail)
                    res.append(None)

            if action in ["snapcheck", "check"]:
                if local and 'local' in config_data:
                    res={}
                    for local_snap in config_data['local']:
                        res[local_snap] = self.get_test(
                                                config_data,
                                                hostname,
                                                pre_name,
                                                post_snap,
                                                action)
                    res = [res]
                else:
                    res = []
                    res.append(
                        self.get_test(
                            config_data,
                            hostname,
                            pre_name,
                            post_snap,
                            action))
            return res

    def snap(self, data, file_name, dev=None, folder=None):
        """
        Function equivalent to --snap operator, for module version
        :param data: either main config file or string containing details of main config file
        :param file_name: snap file, either complete filename or file tag
        :param dev: device object
        :param folder: custom directory path to use for lookup
        """
        DirStore.custom_dir = folder
        if isinstance(dev, Device):
            res = self.extract_dev_data(dev, data, file_name, "snap")
        else:
            res = self.extract_data(data, file_name, "snap")
        return res

    def snapcheck(self, data, file_name=None, dev=None, local= False, folder=None):
        """
        Function equivalent to --snapcheck operator, for module version
        :param data: either main config file or string containing details of main config file
        :param pre_file: pre snap file, either complete filename or file tag
        :param dev: device object
        :param folder: custom directory path to use for lookup
        :return: return list of object of testop.Operator containing test details or list of dictionary of object of testop.Operator containing test details for each stored snapshot
        """
        DirStore.custom_dir = folder
        if file_name is None:
            file_name = "snap_temp"
            self.snap_del = True
        if isinstance(dev, Device):
            res = self.extract_dev_data(dev, data, file_name, "snapcheck", local=local)
        else:
            res = self.extract_data(data, file_name, "snapcheck", local=local)
        return res

    def check(self, data, pre_file=None, post_file=None, dev=None, folder=None):
        """
        Function equivalent to --check operator, for module version
        :param data: either main config file or string containing details of main config file
        :param pre_file: pre snap file, either complete filename or file tag
        :param post_file: post snap file, either complete filename or file tag
        :param dev: device object
        :param folder: custom directory path to use for lookup
        :return: return object of testop.Operator containing test details
        """
        DirStore.custom_dir = folder
        if isinstance(dev, Device):
            res = self.extract_dev_data(
                dev,
                data,
                pre_file,
                "check",
                post_file)
        else:
            res = self.extract_data(data, pre_file, "check", post_file)
        return res

    #######  generate init folder ######
    '''
    def generate_init(self):

        create snapshots and configs folder along with sample main config file.
        All snapshots generated will go in snapshots folder. configs folder will contain
        all the yaml file apart from main, like device.yml, bgp_neighbor.yml
        :return:

        mssg= "Creating Jsnapy directory structure at:" + os.getcwd()
        self.logger.debug(colorama.Fore.BLUE + mssg)
        if not os.path.isdir("snapshots"):
            os.mkdir("snapshots")
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        dst_config_path = os.path.join(os.getcwd(), 'configs')
        # overwrite files if given option -o or --overwrite
        if not os.path.isdir(dst_config_path) or self.args.overwrite is True:
            distutils.dir_util.copy_tree(os.path.join(os.path.dirname(__file__), 'configs'),
                                         dst_config_path)
        dst_main_yml = os.path.join(dst_config_path, 'main.yml')
        if not os.path.isfile(
                os.path.join(os.getcwd(), 'main.yml')) or self.args.overwrite is True:
            shutil.copy(dst_main_yml, os.getcwd())

        logging_yml_file = os.path.join(
            os.path.dirname(__file__),
            'logging.yml')
        if not os.path.isfile(
                os.path.join(os.getcwd(), 'logging.yml')) or self.args.overwrite is True:
            shutil.copy(logging_yml_file, os.getcwd())
        mssg1= "Jsnap folders created at: " + os.getcwd()
        self.logger.info(colorama.Fore.BLUE + mssg1)
    '''

    def check_arguments(self):
        """
        checks combination of arguments given from command line and display help if correct
        set of combination is not given.
        :return: print message in command line, regarding correct usage of JSNAPy
        """
        ## only four test operation is permitted, if given anything apart from this, then it should print error message
        if (self.args.snap is False and self.args.snapcheck is False and self.args.check is False and self.args.diff is False and self.args.version is False):
            self.logger.error(colorama.Fore.RED +
                              "Arguments not given correctly, Please refer help message", extra=self.log_detail)
            self.parser.print_help()
            sys.exit(1)

        if(((self.args.snap is True and (self.args.pre_snapfile is None or self.args.file is None)) or
            (self.args.snapcheck is True and self.args.file is None) or
            (self.args.check is True and self.args.file is None)) and 
            (self.args.testfiles is None or self.args.hostname is None)
           ):
            self.logger.error(colorama.Fore.RED +
                              "Arguments not given correctly, Please refer help message", extra=self.log_detail)
            self.parser.print_help()
            sys.exit(1)
        if self.args.diff is True:
            if (self.args.pre_snapfile is not None and os.path.isfile(self.args.pre_snapfile)) and (
                    self.args.post_snapfile is not None and os.path.isfile(self.args.post_snapfile)):
                comp = Comparator()
                comp.compare_diff(
                    self.args.pre_snapfile,
                    self.args.post_snapfile,
                    None)
                sys.exit(1)
            else:
                if (self.args.file is None) and (
                    self.args.testfiles is None or self.args.hostname is None):
                    self.parser.print_help()
                    sys.exit(1)


def main():
    js = SnapAdmin()
    if len(sys.argv) == 1:
        js.parser.print_help()
        sys.exit(1)
    else:
        js.check_arguments()
        if js.args.version is True:
            print ("JSNAPy version: %s" % version.__version__)
        else:
            if js.args.verbosity:
                js.set_verbosity(10*js.args.verbosity)
            try:
                js.get_hosts()
            except yaml.scanner.ScannerError as ex:
                js.logger.error(colorama.Fore.RED +
                                "ERROR!! YAML file not defined properly, \nComplete Message: %s" % str(ex), extra=js.log_detail)
            except Exception as ex:
                js.logger.error(colorama.Fore.RED +
                                "ERROR!! %s \nComplete Message:  %s" % (type(ex).__name__, str(ex)), extra=js.log_detail)

if __name__ == '__main__':
    main()
