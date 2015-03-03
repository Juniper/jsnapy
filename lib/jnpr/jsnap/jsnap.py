#!/usr/bin/env python

import yaml
import argparse
from hosts import Hosts
from snap import Parse
from check import Comparator
from testop import Operator
import os

class Jsnap:

    def __init__(self):
        global args
        self.parser = argparse.ArgumentParser()
        group = self.parser.add_mutually_exclusive_group()
        # for mutually exclusive gp, can not use both options
        group.add_argument(
            '--snap',
            action='store_true',
            help="take the snapshot")
        group.add_argument(
            '--check',
            action='store_true',
            help=" compare snapshots")
        group.add_argument(
            '--snapcheck',
            action='store_true',
            help='check current snapshot')
        self.parser.add_argument(
            "out_file1",
            help="output file")       # make it optional
        self.parser.add_argument(
            "out_file2",
            nargs='?',
            help="output file",
            type=str)       # make it optional
        self.parser.add_argument(
            "file",
            help="config file to take snapshot",
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

    def get_hosts(self):
        os.chdir('..')
        self.args = self.parser.parse_args()
        config_file = self.args.file
        output_file = self.args.out_file1
        path = os.getcwd()
        conf_file = path + '/' + 'ConfigFiles' + '/' + config_file
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        h = Hosts()
        self.devices = h.login(self.args, main_file, output_file)
        self.host_list = h.hostname_list
        return main_file

    def generate_rpc_reply(self, main_file):
        test_files = []
        for mfile in main_file['tests']:
            test_file = open(mfile, 'r')
            test_files.append(yaml.load(test_file))

        g = Parse()
        for tests in test_files:
            g.generate_reply(tests, self.devices)

    def compare_tests(self, main_file):
        comp = Comparator()
        chk = d.args.check
        if (chk):
            comp.generate_test_files(
                main_file,
                self.host_list,
                chk,
                self.args.out_file1,
                self.args.out_file2)
        else:
            comp.generate_test_files(
                main_file,
                self.host_list,
                chk,
                self.args.out_file1)


d = Jsnap()
mainfile = d.get_hosts()
if d.args.snap is True:
    d.generate_rpc_reply(mainfile)
if d.args.check is True or d.args.snapcheck is True:
    d.compare_tests(mainfile)
    obj= Operator()
    obj.final_result()

