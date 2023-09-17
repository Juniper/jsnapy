# from contextlib import nested
from contextlib import contextmanager
from io import StringIO
from jnpr.jsnapy import version
from jnpr.jsnapy.jsnapy import SnapAdmin
from jnpr.junos.device import Device
from nose.plugins.attrib import attr

from unittest.mock import patch, MagicMock, call, ANY

import argparse
import os
import sys
import unittest
import yaml

# try: input = raw_input
# except NameError: pass

if sys.version < '3':
    builtin_string = '__builtin__.raw_'
else:
    builtin_string = 'builtins.'

@contextmanager
def input(arg):
    with patch("sys.stdin", StringIO(f"{arg}")):
        yield

@contextmanager
def secret_input(arg):
    with patch("getpass.getpass", side_effect=arg):
        yield

@attr('unit')
class TestSnapAdmin(unittest.TestCase):
    def setUp(self):
        self.diff = False
        self.hostname = "1.1.1.1"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""
        self.db['first_snap_id'] = None
        self.db['second_snap_id'] = None

    def set_hardcoded_value_for_device(self, js):
        """
        The function set some hardcoded values to passed SnapAdmin instance
        :param js: an instance of SnapAdmin
        """
        js.args.hostname = '1.1.1.1'
        js.args.login = 'abc'
        js.args.passwd = '123'

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')
    def test_main_no_arguments(self, mock_help, mock_exit):
        # assert that if no arguments passed in main, will print help and exit
        from jnpr.jsnapy.jsnapy import main
        main()
        mock_help.assert_called()
        mock_exit.assert_called_with(1)

    @patch('jnpr.jsnapy.SnapAdmin.check_arguments')
    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')
    def test_main_with_arguments_check_version(self, mock_help, mock_check):
        # assert that if arguments are passed with version as one of the argument
        # then it will print version and exit
        from jnpr.jsnapy.jsnapy import main
        sys.argv = ["snap", "--version"]
        main()
        self.assertFalse(mock_help.called)
        self.assertFalse(mock_check.called)

    @patch('jnpr.jsnapy.SnapAdmin.check_arguments')
    @patch('jnpr.jsnapy.SnapAdmin.start_process')
    def test_main_with_arguments_check_verbosity(self, mock_check, mock_process):
        # test to assert that if arguments are passed properly it will work fine.
        # Added verbosity as the parameter
        from jnpr.jsnapy.jsnapy import main
        sys.argv = ["--snapcheck", "pre", "post", "-f", "main.yml", "-v"]
        main()
        self.assertTrue(mock_check.called)
        self.assertTrue(mock_process.called)

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.SnapAdmin.check_arguments')
    def test_main_exception_yaml_file_parsing(self, mock_check, mock_exit):
        # assert that if there is an error in parsing the YAML file,
        # An exception is raised in the main and it exits.
        from jnpr.jsnapy.jsnapy import main
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_false_keyError.yml')
        sys.argv = ["--snapcheck", "pre", "post", "-f", conf_file, "-v"]
        self.assertRaises(TypeError, main())

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')
    def test_check_arguments_wrong_operation(self, mock_help, mock_exit):
        # assert that if correct operation is not passed it will print help and exit
        js = SnapAdmin()
        js.args.snap = False
        js.args.snapcheck = False
        js.args.diff = False
        js.args.check = False
        js.check_arguments()
        mock_help.assert_called()
        mock_exit.assert_called_with(1)

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')
    def test_check_arguments_operation_lesser_parameter(self, mock_help, mock_exit):
        # if correct number of argument is not passed it will print help and exit
        js = SnapAdmin()
        js.args.snapcheck = True
        js.check_arguments()
        mock_help.assert_called()
        mock_exit.assert_called_with(1)

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')
    def test_check_arguments_diff_operation(self, mock_help, mock_exit):
        # check arguments for diff operation
        js = SnapAdmin()
        js.args.diff = True
        js.args.file = "main.yml"
        js.check_arguments()
        self.assertFalse(mock_exit.called)
        self.assertFalse(mock_help.called)

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')
    def test_check_arguments_check_operation(self, mock_help, mock_exit):
        # check arguments for check operation
        js = SnapAdmin()
        js.args.check = True
        js.args.file = "main.yml"
        js.args.pre_snapfile = "pre"
        js.args.post_snapfile = "post"
        js.check_arguments()
        self.assertFalse(mock_exit.called)
        self.assertFalse(mock_help.called)

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')
    def test_check_arguments_snapcheck_operation(self, mock_help, mock_exit):
        # check arguments for snapcheck operation
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main.yml"
        js.check_arguments()
        self.assertFalse(mock_exit.called)
        self.assertFalse(mock_help.called)

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')
    def test_check_arguments_snap_operation(self, mock_help, mock_exit):
        # check arguments for snap operation
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main.yml"
        js.check_arguments()
        self.assertFalse(mock_exit.called)
        self.assertFalse(mock_help.called)

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    def test_get_config_file_no_file(self, mock_exit):
        js = SnapAdmin()
        js.main_file = "hosts"
        js.args.file = "file_not_found.yml"
        js.get_config_file()
        mock_exit.assert_called_with(1)

    def test_get_config_file_from_file_exact_path(self):
        # config file is extracted when exact path is passed
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main.yml')
        js.get_config_file()
        config_file = open(js.args.file, 'r')
        config_file = yaml.load(config_file, Loader=yaml.FullLoader)
        self.assertEqual(js.main_file, config_file)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_get_config_file_from_file_with_default_path(self, mock_path):
        # config file to be appended with default path when file not present in the path.
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js = SnapAdmin()
        js.args.file = "main.yml"
        js.get_config_file()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main.yml')
        config_file = open(conf_file, 'r')
        config_file = yaml.load(config_file, Loader=yaml.FullLoader)
        self.assertEqual(js.main_file, config_file)

    def test_get_config_file_from_arguments(self):
        js = SnapAdmin()
        self.set_hardcoded_value_for_device(js)
        js.args.testfiles = ["main.yml"]
        js.get_config_file()
        local_dict = {'hosts': [{'device': '1.1.1.1', 'username': 'abc', 'passwd': '123'}], 'tests': ['main.yml']}
        self.assertEqual(js.main_file, local_dict)

    @patch('jnpr.jsnapy.jsnapy.Comparator')
    def test_check_diff_as_arg_test_empty_file(self, mock_comp):
        js = SnapAdmin()
        js.args.diff = True
        js.args.pre_snapfile = "first_file.xml"
        js.args.post_snapfile = "second_file.xml"
        js.check_diff_as_arg()
        self.assertFalse(mock_comp.called)

    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.Comparator')
    def test_check_diff_as_arg_test_file(self, mock_comp, mock_exit):
        js = SnapAdmin()
        js.args.diff = True
        js.args.pre_snapfile = os.path.join(os.path.dirname(__file__),
                                            'configs', '1.1.1.1_snap_not-range_pre_show_chassis_fpc.xml')
        js.args.post_snapfile = os.path.join(os.path.dirname(__file__),
                                             'configs', '1.1.1.1_snap_is-lt_pre_show_chassis_fpc.xml')
        js.check_diff_as_arg()
        self.assertTrue(mock_comp.called)

    def test_extract_device_information_from_file(self):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        js.main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        host_dict = {}
        js.extract_device_information(host_dict)
        hosts = ['1.1.1.1']
        self.assertEqual(js.host_list, hosts)

    def test_extract_device_information_from_arguments(self):
        js = SnapAdmin()
        self.set_hardcoded_value_for_device(js)
        host_dict = {}
        js.extract_device_information(host_dict)
        hosts = ['1.1.1.1']
        self.assertEqual(js.host_list, hosts)

    @patch('logging.Logger.error')
    def test_extract_device_information_keyerror(self, mock_log):
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_false_keyError.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        host_dict = {}
        js.extract_device_information(host_dict)
        mock_log.assert_called_with("\x1b[31m\nERROR occurred !! Hostname not given properly 'hosts'",
                                    extra={'hostname': None})

    @patch('logging.Logger.error')
    def test_extract_device_information_empty_mainfile(self, mock_log):
        js = SnapAdmin()
        js.main_file = None
        host_dict = {}
        js.extract_device_information(host_dict)
        mock_log.assert_called_with("\x1b[31m\nERROR occurred !! 'NoneType' object is not subscriptable",
                                    extra={'hostname': None})

    @patch('logging.Logger.error')
    def test_extract_device_information_attribute_error(self, mock_log):
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_false_keyError_device.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        host_dict = {}
        js.extract_device_information(host_dict)
        mock_log.assert_called_with("\x1b[31mERROR!! KeyError 'device' key not found", extra={'hostname': None})

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.jsnapy.Parser')
    def test_generate_rpc_reply_correct_data(self, mock_parse, mock_path):
        # Testcase to check if proper config_data is passed to generate_rpc_reply
        # it should not give an error in that function
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace()
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.test_cases = None
        js.generate_rpc_reply(
            None,
            "snap_mock",
            "1.1.1.1",
            js.main_file)
        self.assertTrue(mock_parse.called)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.extract_test_cases')
    @patch('jnpr.jsnapy.jsnapy.Parser')
    def test_generate_rpc_reply_testcase_extracted_data(self, mock_parse, mock_extract, mock_path):
        # Testcase to check if proper config_data is passed to generate_rpc_reply
        # testcases is already extracted so it should not be called.
        # it should not give an error in that function
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace()
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.test_cases = [{'tests_include': ['check_chassis_fpc'], 'check_chassis_fpc':
            [{'command': 'show chassis fpc'}, {'item': {'xpath': '//fpc', 'id': 'slot',
                                                        'tests': [{'delta': 'memory-heap-utilization, 50%'}]}}]}]
        js.generate_rpc_reply(
            None,
            "snap_mock",
            "1.1.1.1",
            js.main_file)
        self.assertFalse(mock_extract.called)
        self.assertTrue(mock_parse.called)

    def test_extract_test_cases_wrong_path(self):
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        data = js.extract_test_cases(js.main_file)
        self.assertEqual(data, [])

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.connect')
    def test_extract_data_text_string(self, mock_connect):
        js = SnapAdmin()
        config_data = """
                hosts:
                  - device: 1.1.1.1
                    username : abc
                    passwd: xyz
                tests:
                  - test_anything.yml
                """
        js.snapcheck(config_data, 'mock_pre')
        config_data = yaml.load(config_data, Loader=yaml.FullLoader)
        mock_connect.assert_called_with('1.1.1.1', 'abc', 'xyz', 'mock_pre', config_data, 'snapcheck', None)

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.connect')
    def test_snapcheck_no_file_passed(self, mock_connect):
        js = SnapAdmin()
        config_data = """
                hosts:
                  - device: 1.1.1.1
                    username : abc
                    passwd: xyz
                tests:
                  - test_anything.yml
                """
        js.snapcheck(config_data)
        config_data = yaml.load(config_data, Loader=yaml.FullLoader)
        mock_connect.assert_called_with('1.1.1.1', 'abc', 'xyz', 'snap_temp', config_data, 'snapcheck', None)

    def test_extract_data_error(self):
        with self.assertRaises(Exception):
            js = SnapAdmin()
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'no_such_file.yml')
            js.extract_data(js.args.file, 'mock_pre', None, 'mock_post')

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.chk_database')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.connect')
    def test_extract_data_check_database(self, mock_connect, mock_chkdb):
        js = SnapAdmin()
        config_data = """
                    hosts:
                      - device: 1.1.1.1
                        username : abc
                        passwd: xyz
                    tests:
                      - test_anything.yml
                    sqlite:
                      - store_in_sqlite: True
                        database_name: jbb.db
                        check_from_sqlite: True
                        compare: 1,0
                    """
        js.snapcheck(config_data, 'mock_pre')
        config_data = yaml.load(config_data, Loader=yaml.FullLoader)
        mock_chkdb.assert_called()
        mock_connect.assert_called_with('1.1.1.1', 'abc', 'xyz', 'mock_pre', config_data, 'snapcheck', None)

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.get_test')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.generate_rpc_reply')
    def test_extract_dev_data_from_file(self, mock_gen_rpc, mock_dev, mock_path, mock_test):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__), 'configs', 'main_1.yml')
        config_file = open(conf_file, 'r')
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.snapcheck(config_data, 'mock_pre', dev)
        mock_gen_rpc.assert_called_with(dev, 'mock_pre', 'abc', config_data)
        mock_test.assert_called()

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.get_test')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.generate_rpc_reply')
    def test_extract_dev_data_from_file_and_local(self, mock_gen_rpc, mock_dev, mock_path, mock_test):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__), 'configs', 'main_local.yml')
        config_file = open(conf_file, 'r')
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.snapcheck(config_data, 'mock_pre', dev)
        self.assertFalse(mock_gen_rpc.called)
        mock_test.assert_called()

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('ncclient.manager.connect')
    def test_extract_dev_data_device_closed(self, mock_dev, mock_path):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        with self.assertRaises(Exception):
            dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
            dev.open()
            dev.close()
            js = SnapAdmin()
            js.args.file = 'main_local.yml'
            js.snapcheck(js.args.file, 'mock_pre', dev)

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.get_test')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.generate_rpc_reply')
    def test_extract_dev_data_dictionary_based_data(self, mock_gen_rpc, mock_dev, mock_path, mock_test):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__), 'configs', 'main_1.yml')
        config_file = open(conf_file, 'r')
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.snapcheck(config_data, 'mock_pre', dev)
        mock_gen_rpc.assert_called_with(dev, 'mock_pre', 'abc', config_data)
        mock_test.assert_called()

    @patch('ncclient.manager.connect')
    def test_extract_dev_data_invalid_config_data(self, mock_connect):
        with self.assertRaises(SystemExit):
            dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
            dev.open()
            js = SnapAdmin()
            config_data = 1  # config_data no meaning
            js.snapcheck(config_data, 'mock_pre', dev)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_start_process_complete_flow_cmd_line_files(self, mock_connect, mock_path):
        # Testcase to check complete call flow till connect when data passed in command line as files
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main_1.yml"
        js.args.pre_snapfile = "pre"
        js.args.post_snapfile = "post"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()

        expected_calls_made = [call('1.1.1.1', 'abc', 'xyz', 'pre', ANY, ANY, ANY)]

        self.assertTrue(mock_connect.called)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_start_process_complete_flow_cmd_line_files_multiple_device(self, mock_connect, mock_path):
        # Testcase to check complete call flow till connect when data passed in command line as files
        # with multiple devices in the yml file
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main_6.yml"
        js.args.pre_snapfile = "pre"
        js.args.post_snapfile = "post"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()

        expected_calls_made = [call('1.1.1.1', 'abc', 'xyz', 'pre', ANY, ANY, ANY),
                               call('1.1.1.15', 'abc', 'xyz', 'pre', ANY, ANY, ANY),
                               call('1.1.1.16', 'abc', 'xyz', 'pre', ANY, ANY, ANY),
                               ]

        self.assertTrue(mock_connect.called)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_start_process_complete_flow_cmd_line_files_group_based(self, mock_connect, mock_path):
        # Testcase to check complete call flow till connect when data passed in command line as files
        # with multiple devices in the yml file but group based
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main1.yml"
        js.args.pre_snapfile = "pre"
        js.args.post_snapfile = "post"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()

        expected_calls_made = [call('1.1.1.3', 'abc', 'def', 'pre', ANY, ANY, ANY),
                               call('1.1.1.4', 'abc', 'def', 'pre', ANY, ANY, ANY),
                               call('1.1.1.5', 'abc', 'def', 'pre', ANY, ANY, ANY),
                               ]
        self.assertTrue(mock_connect.called)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_start_process_complete_flow_cmd_line_files_multiple_group_based(self, mock_connect, mock_path):
        # Testcase to check complete call flow till connect when data passed in command line as files
        # with multiple devices in the yml file but multiple group based
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main_multiple_group.yml"
        js.args.pre_snapfile = "pre"
        js.args.post_snapfile = "post"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()

        expected_calls_made = [call('1.1.1.3', 'abc', 'def', 'pre', ANY, ANY, ANY),
                               call('1.1.1.4', 'abc', 'def', 'pre', ANY, ANY, ANY),
                               call('1.1.1.5', 'abc', 'def', 'pre', ANY, ANY, ANY),
                               call('1.1.1.6', 'abc', 'def', 'pre', ANY, ANY, ANY),
                               call('1.1.1.12', 'abc', 'def', 'pre', ANY, ANY, ANY),
                               ]
        self.assertTrue(mock_connect.called)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_start_process_complete_flow_with_port_in_file(self, mock_connect, mock_path):
        # Testcase to check complete call flow till connect when data passed in command line as files
        # with port present in file
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main_with_port.yml"
        js.args.pre_snapfile = "pre"
        js.args.post_snapfile = "post"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()

        expected_calls_made = [call('1.1.1.1', 'abc', 'xyz', 'pre', ANY, ANY, ANY, port=44)]
        self.assertTrue(mock_connect.called)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_start_process_complete_flow_with_port_in_file_group_based(self, mock_connect, mock_path):
        # Testcase to check complete call flow till connect when data passed in command line as files
        # with port present in file based on group
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main2_with_port.yml"
        js.args.pre_snapfile = "pre"
        js.args.post_snapfile = "post"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()

        expected_calls_made = [call('1.1.1.3', 'abc', 'def', 'pre', ANY, ANY, ANY, port=100),
                               call('1.1.1.4', 'abc', 'def', 'pre', ANY, ANY, ANY, port=101),
                               call('1.1.1.5', 'abc', 'def', 'pre', ANY, ANY, ANY, port=102),
                               ]
        self.assertTrue(mock_connect.called)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_start_process_complete_flow_with_port_as_arg(self, mock_connect, mock_path):
        # Testcase to check complete call flow till connect when data passed in command line as files
        # with port present in file and in argument. Port in argument should have higher importance
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = "main2_with_port.yml"
        js.args.pre_snapfile = "pre"
        js.args.post_snapfile = "post"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.args.port = 55
        js.start_process()

        expected_calls_made = [call('1.1.1.3', 'abc', 'def', 'pre', ANY, ANY, ANY, port=55),
                               call('1.1.1.4', 'abc', 'def', 'pre', ANY, ANY, ANY, port=55),
                               call('1.1.1.5', 'abc', 'def', 'pre', ANY, ANY, ANY, port=55),
                               ]
        self.assertTrue(mock_connect.called)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.api_based_handling')
    def test_snap(self, mock_data):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        config_file = open(js.args.file, 'r')
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.snap(js.args.file, 'mock_file')
        mock_data.assert_called_with(data, 'mock_file', "snap", None, local=False)

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.api_based_handling')
    def test_check(self, mock_data):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        config_file = open(js.args.file, 'r')
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.check(js.args.file, 'mock_file')
        mock_data.assert_called_with(data, 'mock_file', "check", None, local=False)

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.api_based_handling')
    def test_snapcheck(self, mock_data):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        config_file = open(js.args.file, 'r')
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.snapcheck(js.args.file, 'mock_file')
        mock_data.assert_called_with(data, 'mock_file', "snapcheck", None, local=False)

    @patch('sys.exit')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.api_based_handling')
    def test_action_api_based_error_file(self, mock_data, mock_exit):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        js.snapcheck(js.args.file, 'mock_file')
        mock_exit.assert_called

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.api_based_handling')
    def test_action_api_based_data_passed_in_string(self, mock_data):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        config_file = open(js.args.file, 'r')
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.snapcheck(data, 'mock_file')
        mock_data.assert_called_with(data, 'mock_file', "snapcheck", None, local=False)

    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.api_based_handling_with_dev')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.api_based_handling')
    def test_action_api_based_data_passed_in_string_with_device(self, mock_data, mock_dev_data,
                                                                mock_connect):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        config_file = open(js.args.file, 'r')
        data = yaml.load(config_file, Loader=yaml.FullLoader)
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        js.snapcheck(data, 'mock_file', dev)
        self.assertFalse(mock_data.called)
        self.assertTrue(mock_dev_data.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect_multiple_device')
    def test_sqlite_parameters_for_snap_not_checked(self, mock_mul_dev, mock_exit):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        js.args.snap = True
        js.args.pre_snapfile = "mock_snap"
        js.start_process()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect_multiple_device')
    def test_sqlite_parameters_for_check_not_checked(self, mock_mul_dev, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        js.args.check = True
        js.args.pre_snapfile = "mock_snap"
        js.args.post_snapfile = "mock_snap2"
        js.start_process()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect_multiple_device')
    def test_sqlite_parameters_for_snap(self, mock_mul_dev, mock_exit):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_2.yml')
        js.args.snap = True
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        js.start_process()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect_multiple_device')
    def test_sqlite_parameters_for_check(self, mock_mul_dev, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_11.yml')
        js.args.check = True
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        self.db['first_snap_id'] = 1
        self.db['second_snap_id'] = 0
        js.start_process()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect_multiple_device')
    def test_sqlite_parameters_for_check_different_snap_id(self, mock_mul_dev, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_4.yml')
        js.args.check = True
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        self.db['first_snap_id'] = 0
        self.db['second_snap_id'] = 1
        js.start_process()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect_multiple_device')
    def test_sqlite_parameters_for_check_chksqlite(self, mock_mul_dev, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_5.yml')
        js.args.check = True
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        self.db['first_snap_id'] = 0
        self.db['second_snap_id'] = 1
        js.start_process()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect_multiple_device')
    def test_sqlite_parameters_for_snapcheck_strsqlite(self, mock_mul_dev, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_2.yml')
        js.args.snapcheck = True
        js.args.diff = False
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        js.start_process()
        self.assertEqual(js.db, self.db)

    def test_chk_database_1(self):
        with self.assertRaises(SystemExit):
            js = SnapAdmin()
            js.db['store_in_sqlite'] = True
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
            config_file = open(js.args.file, 'r')
            config_data = yaml.load(config_file, Loader=yaml.FullLoader)
            del (config_data['sqlite'][0]['database_name'])  # either we could have a config file with no db name
            del (config_data['sqlite'][0]['store_in_sqlite'])
            del (config_data['sqlite'][0]['check_from_sqlite'])
            js.chk_database(config_data, 'mock_pre', 'mock_post')  # or we could delete the key value pair

    def test_chk_database_2(self):
        with self.assertRaises(SystemExit):
            js = SnapAdmin()
            js.db['store_in_sqlite'] = True
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
            config_file = open(js.args.file, 'r')
            config_data = yaml.load(config_file, Loader=yaml.FullLoader)
            del (config_data['sqlite'][0]['store_in_sqlite'])
            del (config_data['sqlite'][0]['check_from_sqlite'])
            config_data['sqlite'][0]['compare'] = 0
            js.chk_database(config_data, 'mock_pre', 'mock_post', check=True)

    def test_chk_database_3(self):
        with self.assertRaises(SystemExit):
            js = SnapAdmin()
            js.db['store_in_sqlite'] = True
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
            config_file = open(js.args.file, 'r')
            config_data = yaml.load(config_file, Loader=yaml.FullLoader)
            del (config_data['sqlite'][0]['store_in_sqlite'])
            del (config_data['sqlite'][0]['check_from_sqlite'])
            config_data['sqlite'][0]['compare'] = 'ab'
            js.chk_database(config_data, 'mock_pre', 'mock_post', check=True)

    def test_chk_database_4(self):
        with self.assertRaises(SystemExit):
            js = SnapAdmin()
            js.db['store_in_sqlite'] = True
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
            config_file = open(js.args.file, 'r')
            config_data = yaml.load(config_file, Loader=yaml.FullLoader)
            del (config_data['sqlite'][0]['store_in_sqlite'])
            del (config_data['sqlite'][0]['check_from_sqlite'])
            config_data['sqlite'][0]['compare'] = '0,1,2'
            js.chk_database(config_data, 'mock_pre', 'mock_post', check=True)

    def test_chk_database_5(self):
        with self.assertRaises(SystemExit):
            js = SnapAdmin()
            js.db['store_in_sqlite'] = True
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
            config_file = open(js.args.file, 'r')
            config_data = yaml.load(config_file, Loader=yaml.FullLoader)
            del (config_data['sqlite'][0]['store_in_sqlite'])
            del (config_data['sqlite'][0]['check_from_sqlite'])
            config_data['sqlite'][0]['compare'] = '0'
            js.chk_database(config_data, 'mock_pre', 'mock_post', check=True)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_check_mail(self, mock_path, mock_notify, mock_pass, mock_compare, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail_2.yml')
        js.args.check = True
        js.args.snap = False
        js.args.snapcheck = False
        js.args.pre_snapfile = "mock_snap"
        js.args.post_snapfile = "mock_snap2"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()
        self.assertTrue(mock_notify.called)
        self.assertTrue(mock_pass.called)
        self.assertTrue(mock_compare.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_snapcheck_mail(
            self, mock_path, mock_getlogger, mock_notify, mock_pass, mock_compare, mock_reply, mock_dev, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail_2.yml')
        js.args.snapcheck = True
        js.args.pre_snapfile = "mock_snap"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()
        self.assertTrue(mock_notify.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_snap_mail(self, mock_logger, mock_notify, mock_pass, mock_compare, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail.yml')
        js.args.snap = True
        js.args.pre_snapfile = "mock_snap"
        js.start_process()
        self.assertFalse(mock_notify.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_check_mail_password(
            self, mock_path, mock_notify, mock_pass, mock_compare, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail_2.yml')
        js.args.check = True
        js.args.pre_snapfile = "mock_snap"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js.start_process()
        self.assertTrue(mock_pass.called)
        self.assertTrue(mock_notify.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_conditional_mail_1(self, mock_path, mock_notify, mock_pass, mock_compare, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail_condition.yml')
        js.args.check = True
        js.args.snap = False
        js.args.snapcheck = False
        js.args.pre_snapfile = "mock_snap"
        js.args.post_snapfile = "mock_snap2"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_compare.return_value = MagicMock(result='Failed')

        js.start_process()
        self.assertTrue(mock_notify.called)
        self.assertTrue(mock_pass.called)
        self.assertTrue(mock_compare.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_conditional_mail_2(self, mock_path, mock_notify, mock_pass, mock_compare, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail_condition.yml')
        js.args.diff = True
        js.args.check = False
        js.args.snap = False
        js.args.snapcheck = False
        js.args.pre_snapfile = "mock_snap"
        js.args.post_snapfile = "mock_snap2"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_compare.return_value = MagicMock(result='Failed')

        js.start_process()
        self.assertFalse(mock_notify.called)
        self.assertFalse(mock_pass.called)
        self.assertTrue(mock_compare.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_conditional_mail_3(self, mock_path, mock_notify, mock_pass, mock_compare, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail_condition.yml')
        js.args.check = True
        js.args.snap = False
        js.args.snapcheck = False
        js.args.pre_snapfile = "mock_snap"
        js.args.post_snapfile = "mock_snap2"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_compare.return_value = MagicMock(result='Passed')

        js.start_process()
        self.assertTrue(mock_notify.called)
        self.assertFalse(mock_pass.called)
        self.assertTrue(mock_compare.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_conditional_mail_4(self, mock_path, mock_notify, mock_pass, mock_compare, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail_incomplete_condition.yml')
        js.args.check = True
        js.args.snap = False
        js.args.snapcheck = False
        js.args.pre_snapfile = "mock_snap"
        js.args.post_snapfile = "mock_snap2"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_compare.return_value = MagicMock(result='Failed')

        js.start_process()
        self.assertFalse(mock_notify.called)
        self.assertFalse(mock_pass.called)
        self.assertTrue(mock_compare.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_conditional_mail_5(self, mock_path, mock_notify, mock_pass, mock_compare, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_mail_wrong.yml')
        js.args.check = True
        js.args.snap = False
        js.args.snapcheck = False
        js.args.pre_snapfile = "mock_snap"
        js.args.post_snapfile = "mock_snap2"
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_compare.return_value = MagicMock(result='Passed')

        js.start_process()
        self.assertFalse(mock_notify.called)
        self.assertFalse(mock_pass.called)
        self.assertTrue(mock_compare.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    def test_operation_diff(self, mock_compare, arg_exit):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.args.diff = True
        js.args.pre_snapfile = "mock_snap1"
        js.args.post_snapfile = "mock_snap2"
        js.start_process()
        mock_compare.assert_called_once_with(
            '1.1.1.1',
            config_data,
            js.args.pre_snapfile,
            None,
            'diff')

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('jnpr.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_operation_snapcheck(
            self, mock_log, mock_snap, mock_check, mock_dev, mock_arg):
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.args.pre_snapfile = "mock_snap"
        js.start_process()
        self.assertTrue(mock_snap.called)
        self.assertTrue(mock_dev.called)
        mock_check.assert_called_once_with(
            '1.1.1.1',
            config_data,
            js.args.pre_snapfile,
            None,
            'snapcheck')

    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('jnpr.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_operation_snapcheck_local_config(
            self, mock_log, mock_snap, mock_check, mock_dev):
        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_local_snapcheck.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
        js.args.pre_snapfile = "mock_snap"
        js.start_process()
        self.assertTrue(js.args.local)
        self.assertFalse(mock_dev.called)
        self.assertFalse(mock_snap.called)
        # we check whether get_test was called, indirectly checking whether compare_tests was called.
        expected_calls_made = [call('1.1.1.1', config_data, 'PRE', None, 'snapcheck'),
                               call('1.1.1.1', config_data, 'PRE_42', None, 'snapcheck'),
                               call('1.1.1.1', config_data, 'PRE_314', None, 'snapcheck')
                               ]
        mock_check.assert_has_calls(expected_calls_made, any_order=True)

    def test_get_device_login(self):
        """test getting the password from user"""
        js = SnapAdmin()
        with input("dummy.username"):
            self.assertEqual(js.get_device_login(), "dummy.username")

    def test_get_device_passwd(self):
        """ test getting hidden text from the user """
        js = SnapAdmin()
        with secret_input("a$$w0rd"):
            self.asserEqual(js.get_device_login(), "a$$w0rd")


