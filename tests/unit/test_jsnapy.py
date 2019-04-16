import unittest
import yaml
import os
import sys
from jnpr.jsnapy import version
from jnpr.jsnapy.jsnapy import SnapAdmin
from mock import patch, MagicMock, call
# from contextlib import nested
from nose.plugins.attrib import attr
import argparse
from jnpr.junos.device import Device

# try: input = raw_input
# except NameError: pass

if sys.version < '3':
    builtin_string = '__builtin__.raw_'
else:
    builtin_string = 'builtins.'


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

    @patch('jnpr.jsnapy.jsnapy.Parser')
    def test_snap(self, mock_parse):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace()
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.generate_rpc_reply(
            None,
            "snap_mock",
            "1.1.1.1",
            js.main_file)
        self.assertTrue(mock_parse.called)

    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_hostname(self, mock_connect):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_6.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        expected_calls_made = [call('1.1.1.1', 'abc', 'xyz', 'snap_1'),
                               call('1.1.1.15', 'abc', 'xyz', 'snap_1'),
                               call('1.1.1.16', 'abc', 'xyz', 'snap_1'),
                               ]

        hosts = ['1.1.1.1', '1.1.1.15', '1.1.1.16']
        self.assertEqual(js.host_list, hosts)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_multiple_hostname(self, mock_path, mock_connect, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main1.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        hosts = ['1.1.1.3', '1.1.1.4', '1.1.1.5']
        self.assertEqual(js.host_list, hosts)

        # extending the test to check for device overlap among groups
        js.main_file['hosts'][0]['group'] = 'MX, EX'
        expected_calls_made = [call('1.1.1.3', 'abc', 'def', 'snap_1'),
                               call('1.1.1.4', 'abc', 'def', 'snap_1'),
                               call('1.1.1.5', 'abc', 'def', 'snap_1'),
                               call('1.1.1.6', 'abc', 'def', 'snap_1'),
                               call('1.1.1.12', 'abc', 'def', 'snap_1'),
                               ]

        js.login("snap_1")
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_connect_snap(self, mock_log, mock_gen_reply, mock_dev, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        js.args.snap = True
        js.args.pre_snapfile = "mock_snap"
        js.get_hosts()
        self.assertTrue(mock_gen_reply.called)
        self.assertTrue(mock_dev.called)

    @patch('logging.Logger.error')  # new
    def test_hostname_keyError(self, mock_log):
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_false_keyError.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        self.assertTrue(mock_log.called)
        mock_log.assert_called_with("\x1b[31m\nERROR occurred !! Hostname not given properly 'hosts'",
                                    extra={'hostname': None})

    @patch('logging.Logger.error')  # new
    def test_hostname_keyError_general(self, mock_log):
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_false_keyError.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.main_file = None
        js.login("snap_1")
        self.assertTrue(mock_log.called)
        mock_log.assert_called()

    @patch('logging.Logger.error')  # new
    def test_hostname_keyError_device(self, mock_log):
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_false_keyError_device.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        self.assertTrue(mock_log.called)
        mock_log.assert_called_with("\x1b[31mERROR!! KeyError 'device' key not found", extra={'hostname': None})

    @patch('jnpr.jsnapy.SnapAdmin.connect')  # new
    def test_multiple_hostname_1(self, mock_connect):
        js = SnapAdmin()
        config_file = open('main1.yml', 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        hosts = ['1.1.1.3', '1.1.1.4', '1.1.1.5']
        self.assertEqual(js.host_list, hosts)

    @patch('jnpr.jsnapy.SnapAdmin.connect')  # new
    def test_hostname_hostname_argument(self, mock_connect):
        js = SnapAdmin()
        js.args.hostname = '1.1.1.3'
        js.args.login = 'abc'
        js.args.passwd = 'xyz'
        js.login("snap_1")
        host = ['1.1.1.3']
        self.assertEqual(js.host_list, host)
        self.assertTrue(mock_connect.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    def test_connect_check(self, mock_compare, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        js.args.check = True
        js.args.pre_snapfile = "mock_snap1"
        js.args.post_snapfile = "mock_snap2"
        js.get_hosts()
        mock_compare.assert_called_once_with(
            '1.1.1.1',
            config_data,
            js.args.pre_snapfile,
            None,
            'check')

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('jnpr.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_connect_snapcheck(
            self, mock_log, mock_snap, mock_check, mock_dev, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        js.args.pre_snapfile = "mock_snap"
        js.get_hosts()
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
    def test_connect_snapcheck_local_cmd(
            self, mock_log, mock_snap, mock_check, mock_dev):

        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.local = True
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        js.args.pre_snapfile = "mock_snap"
        js.get_hosts()
        self.assertFalse(mock_dev.called)
        self.assertFalse(mock_snap.called)
        # we check whether get_test was called, indirectly checking whether compare_tests was called.
        mock_check.assert_called_once_with(
            '1.1.1.1',
            config_data,
            "mock_snap",
            None,
            'snapcheck')

    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('jnpr.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_connect_snapcheck_local_config(
            self, mock_log, mock_snap, mock_check, mock_dev):

        js = SnapAdmin()
        js.args.snapcheck = True
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_local_snapcheck.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        js.args.pre_snapfile = "mock_snap"
        js.get_hosts()
        self.assertTrue(js.args.local)
        self.assertFalse(mock_dev.called)
        self.assertFalse(mock_snap.called)
        # we check whether get_test was called, indirectly checking whether compare_tests was called.
        expected_calls_made = [call('1.1.1.1', config_data, 'PRE', None, 'snapcheck'),
                               call('1.1.1.1', config_data, 'PRE_42', None, 'snapcheck'),
                               call('1.1.1.1', config_data, 'PRE_314', None, 'snapcheck')
                               ]
        mock_check.assert_has_calls(expected_calls_made, any_order=True)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    def test_connect_diff(self, mock_compare, arg_exit):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        js.args.diff = True
        js.args.pre_snapfile = "mock_snap1"
        js.args.post_snapfile = "mock_snap2"
        js.get_hosts()
        mock_compare.assert_called_once_with(
            '1.1.1.1',
            config_data,
            js.args.pre_snapfile,
            None,
            None)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_1(self, mock_log, mock_sys, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.check = True
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_2(self, mock_log, mock_login, mock_sys, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snap = False
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_3.yml')
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.post_snapfile = None
        js.args.pre_snapfile = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            js.get_hosts()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_3(self, mock_log, mock_login, mock_sys, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snapcheck = True
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_4(self, mock_log, mock_login, mock_sys, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snap = False
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_3.yml')
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = True
        js.args.post_snapfile = None
        js.args.pre_snapfile = "mock_snap"
        with patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            js.get_hosts()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()

    @patch('sys.exit')
    @patch('logging.Logger.error')  # new
    def test_check_arguments_5(self, mock_log, mock_sys):
        js = SnapAdmin()
        js.args.snap = False
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = False
        js.args.version = False
        with patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()
            mock_log.assert_called_with('\x1b[31mArguments not given correctly, Please refer help message',
                                        extra={'hostname': None})

    @patch('os.path.isfile')
    @patch('sys.exit')
    def test_check_arguments_6(self, mock_sys, mock_isfile):  # new
        js = SnapAdmin()
        js.args.diff = True
        js.args.pre_snapfile = 'mock_pre'
        js.args.post_snapfile = 'mock_post'
        mock_isfile.return_value = True
        with patch('jnpr.jsnapy.check.Comparator.compare_diff') as mock_comp:
            js.check_arguments()
            mock_sys.assert_called_with(1)
            mock_comp.assert_called_with(js.args.pre_snapfile, js.args.post_snapfile, None)

    @patch('sys.exit')
    def test_check_arguments_7(self, mock_sys):  # new
        js = SnapAdmin()
        js.args.diff = True
        js.args.pre_snapfile = None
        js.args.post_snapfile = 'mock_post'
        js.args.file = None
        with patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called()

    @patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help')  # new
    @patch('sys.exit')
    def test_check_arguments_8(self, mock_sys, mock_parser):
        from jnpr.jsnapy.jsnapy import main
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)
        main()
        mock_parser.assert_called()
        mock_sys.assert_called_with(1)

    @patch('jnpr.jsnapy.jsnapy.Device')  # new
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    @patch('sys.exit')
    def test_check_arguments_9(self, mock_sys, mock_log, mock_dev):
        # mock_input.return_value = "abc"
        js = SnapAdmin()
        js.args.snap = True
        js.args.snapcheck = True
        js.args.local = False
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        with patch(builtin_string + 'input', return_value='abc'):
            js.connect('1.1.1.1', None, 'xyz', 'snap_1', config_data)
            # username='abc'
            mock_log.assert_called()
            mock_dev.assert_called_with(host='1.1.1.1', user='abc', passwd='xyz', gather_facts=False)

    @patch('jnpr.jsnapy.jsnapy.Device')  # new
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_10(self, mock_log, mock_dev):
        js = SnapAdmin()
        js.args.snap = True
        js.args.snapcheck = True
        js.args.local = False
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        js.connect('1.1.1.1', 'abc', 'xyz', 'snap_1', config_data)
        mock_log.assert_called()
        mock_dev.assert_called_with(host='1.1.1.1', user='abc', passwd='xyz', gather_facts=False)

    @patch('ncclient.manager.connect')
    @patch('logging.Logger.info')  # new
    def test_check_arguments_11(self, mock_log, mock_dev):
        with self.assertRaises(Exception):
            js = SnapAdmin()
            js.args.snap = True
            js.args.snapcheck = True
            js.args.local = False
            js.args.file = os.path.join(os.path.dirname(__file__),
                                        'configs', 'main_1.yml')
            config_file = open(js.args.file, 'r')
            config_data = yaml.load(config_file)
            mock_dev.side_effect = Exception()
            js.connect('1.1.1.1', 'abc', None, 'snap_1', config_data)

    @patch('os.path.isfile')  # new
    def test_multiple_devices_1(self, mock_isfile):
        mock_isfile.return_value = lambda arg: arg == 'devices.yml'
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        hosts = config_data.get('hosts')
        js.multiple_device_details(hosts, config_data, 'mock_pre', None, 'mock_post')
        hosts_required = ['1.1.1.3', '1.1.1.4', '1.1.1.5']
        self.assertEqual(js.host_list, hosts_required)

    @patch('jnpr.jsnapy.jsnapy.setup_logging.setup_logging')
    @patch('jnpr.jsnapy.jsnapy.get_path')  # new
    @patch('os.path.isfile')
    def test_multiple_devices_2(self,
                                mock_isfile,
                                mock_path, mock_logging):  # testing if devices.yml file is not present in the same folder as the test file
        mock_isfile.return_value = False  # lambda arg: arg == 'devices.yml'
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main1.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        hosts = config_data.get('hosts')
        js.multiple_device_details(hosts, config_data, 'mock_pre', None, 'mock_post')
        hosts_required = ['1.1.1.3', '1.1.1.4', '1.1.1.5']
        self.assertEqual(js.host_list, hosts_required)
        mock_logging.assert_called()

    def test_multiple_devices_3(self):  # new
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_6.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        hosts = config_data.get('hosts')
        js.multiple_device_details(hosts, config_data, 'mock_pre', None, 'mock_post')
        hosts_required = ['1.1.1.1', '1.1.1.15', '1.1.1.16']
        self.assertEqual(js.host_list, hosts_required)

    @patch('logging.Logger.error')  # new
    def test_multiple_devices_4(self, mock_log):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_false_keyError_device.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        hosts = config_data.get('hosts')
        js.multiple_device_details(hosts, config_data, 'mock_pre', None, 'mock_post')
        mock_log.assert_called_with("\x1b[31mERROR!! KeyError 'device' key not found", extra={'hostname': None})

    @patch('ncclient.manager.connect')  # new
    def test_multiple_devices_5(self, mock_dev_connect):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_6.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        hosts = config_data.get('hosts')
        js.multiple_device_details(hosts, config_data, 'mock_pre', 'snap', 'mock_post')
        mock_dev_connect.assert_called()

    @patch('ncclient.manager.connect')  # new
    def test_multiple_devices_6(self, mock_dev_connect):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_6.yml')
        config_file = open(js.args.file, 'r')
        config_data = yaml.load(config_file)
        hosts = config_data.get('hosts')
        js.multiple_device_details(hosts, config_data, 'mock_pre', 'snapcheck', 'mock_post')
        mock_dev_connect.assert_called()

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.multiple_device_details')
    def test_extract_data_1(self, mock_multiple):  # new
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main1.yml')
        js.extract_data(js.args.file, 'mock_pre', None, 'mock_post')
        mock_multiple.assert_called()

    @patch('jnpr.jsnapy.jsnapy.setup_logging.setup_logging')
    @patch('os.path.isfile')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.get_values')  # new
    def test_extract_data_2(self, mock_getvalue, mock_isfile, mock_logging):
        mock_isfile.return_value = False
        js = SnapAdmin()
        config_data = """
            hosts:
              - device: 1.1.1.1
                username : abc
                passwd: xyz
            tests:
              - test_anything.yml
            """
        js.extract_data(config_data, 'mock_pre', None, 'mock_post')
        mock_getvalue.assert_called()
        mock_logging.assert_called()

    @patch('logging.Logger.info')  # new
    def test_extract_data_3(self, mock_log):
        with self.assertRaises(Exception):
            js = SnapAdmin()
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'no_such_file.yml')
            js.extract_data(js.args.file, 'mock_pre', None, 'mock_post')

    @patch('jnpr.jsnapy.jsnapy.setup_logging.setup_logging')
    @patch('os.path.isfile')  # new
    @patch('logging.Logger.info')
    def test_extract_data_4(self, mock_log, mock_isfile, mock_logging):
        with self.assertRaises(SystemExit):
            mock_isfile.return_value = False
            js = SnapAdmin()
            config_data = 1  # config_data which is fraud
            js.extract_data(config_data, 'mock_pre', None, 'mock_post')
            mock_log.assert_called()
            mock_logging.assert_called()

    @patch('jnpr.jsnapy.jsnapy.setup_logging.setup_logging')
    @patch('os.path.isfile')  # new
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.chk_database')
    def test_extract_data_5(self, mock_chkdb, mock_isfile, mock_logging):
        mock_isfile.return_value = False
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
        js.extract_data(config_data, 'mock_pre', None, 'mock_post')
        mock_chkdb.assert_called()
        mock_logging.assert_called()

    @patch('jnpr.jsnapy.jsnapy.setup_logging.setup_logging')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.chk_database')
    @patch('ncclient.manager.connect')
    @patch('os.path.isfile')  # new
    def test_extract_dev_data_1(self, mock_isfile, mock_dev, mock_chkdb, mock_logging):
        mock_isfile.return_value = False
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
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
        js.extract_dev_data(dev, config_data, 'mock_pre', None, 'mock_post')
        mock_chkdb.assert_called()
        mock_logging.assert_called()

    @patch('ncclient.manager.connect')  # new
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.generate_rpc_reply')
    def test_extract_dev_data_2(self, mock_gen_rpc, mock_dev):
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_local.yml')
        js.extract_dev_data(dev, js.args.file, 'mock_pre', 'snap', 'mock_post')
        mock_gen_rpc.assert_called()

    @patch('ncclient.manager.connect')  # new
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.get_test')
    def test_extract_dev_data_3(self, mock_get_test, mock_dev):
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_local.yml')
        js.extract_dev_data(dev, js.args.file, 'mock_pre', 'snapcheck', 'mock_post', local=True)
        mock_get_test.assert_called()

    @patch('ncclient.manager.connect')  # new
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.get_test')
    def test_extract_dev_data_4(self, mock_get_test, mock_dev):
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_local.yml')
        js.extract_dev_data(dev, js.args.file, 'mock_pre', 'snapcheck', 'mock_post', local=False)
        mock_get_test.assert_called()

    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.get_test')
    def test_extract_dev_data_5(self, mock_get_test, mock_dev):
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        mock_dev.assert_called()
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_local.yml')
        data = open(js.args.file, 'r')
        config_data = yaml.load(data)  # providing the data as dictionary
        js.extract_dev_data(dev, config_data, 'mock_pre', 'snapcheck', 'mock_post', local=False)
        mock_get_test.assert_called()

    @patch('jnpr.jsnapy.jsnapy.setup_logging.setup_logging')
    @patch('ncclient.manager.connect')
    @patch('os.path.isfile')
    @patch('logging.Logger.info')
    def test_extract_dev_data_6(self, mock_log, mock_isfile, mock_dev, mock_logging):
        with self.assertRaises(SystemExit):
            mock_isfile.return_value = False
            dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
            dev.open()
            js = SnapAdmin()
            config_data = 1  # config_data no meaning
            js.extract_dev_data(dev, config_data, 'mock_pre', None, 'mock_post')
            mock_log.assert_called()
            mock_logging.assert_called()

    @patch('ncclient.manager.connect')
    def test_extract_dev_data_7(self, mock_dev):
        with self.assertRaises(Exception):
            dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
            dev.open()
            dev.close()
            js = SnapAdmin()
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_local.yml')
            js.extract_dev_data(js.args.file, 'mock_pre', None, 'mock_post')

    @patch('logging.Logger.error')
    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.generate_rpc_reply')
    def test_extract_dev_data_8(self, mock_gen_rpc, mock_dev, mock_log):
        dev = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev.open()
        mock_gen_rpc.side_effect = Exception('gen_rpc')
        mock_dev.assert_called()
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main_local.yml')
        js.extract_dev_data(dev, js.args.file, 'mock_pre', 'snap', 'mock_post')
        mock_log.assert_called()

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.extract_data')
    def test_snap_1(self, mock_extract_data):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        js.snap(js.args.file, 'mock_file')
        mock_extract_data.assert_called_with(js.args.file, 'mock_file', "snap")

    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.extract_dev_data')
    def test_snap_2(self, mock_extract_dev_data, mock_dev):
        dev_obj = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev_obj.open()
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        js.snap(js.args.file, 'mock_file', dev=dev_obj)
        mock_extract_dev_data.assert_called_with(dev_obj, js.args.file, 'mock_file', "snap")

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.extract_data')
    def test_snapcheck_1(self, mock_extract_data):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        js.snapcheck(js.args.file)  # if filename not given func()  sets it to snap_temp
        mock_extract_data.assert_called_with(js.args.file, 'snap_temp', "snapcheck", local=False)

    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.extract_dev_data')
    def test_snapcheck_2(self, mock_extract_dev_data, mock_dev):
        dev_obj = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev_obj.open()
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        js.snapcheck(js.args.file, dev=dev_obj)  # by default local is false here
        mock_extract_dev_data.assert_called_with(dev_obj, js.args.file, 'snap_temp', "snapcheck", local=False)

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.extract_data')
    def test_check_1(self, mock_extract_data):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        js.check(js.args.file, pre_file='mock_pre', post_file='mock_post')
        mock_extract_data.assert_called_with(js.args.file, 'mock_pre', "check", 'mock_post')

    @patch('ncclient.manager.connect')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.extract_dev_data')
    def test_check_2(self, mock_extract_dev_data, mock_dev):
        dev_obj = Device(user='1.1.1.1', host='abc', passwd='xyz')
        dev_obj.open()
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
        js.check(js.args.file, pre_file='mock_pre', post_file='mock_post', dev=dev_obj)
        mock_extract_dev_data.assert_called_with(dev_obj, js.args.file, 'mock_pre', "check", 'mock_post')

    def test_version(self):
        js = SnapAdmin()
        data = js.get_version()
        self.assertEqual(data, version.__version__)

    def test_chk_database_1(self):
        with self.assertRaises(SystemExit):
            js = SnapAdmin()
            js.db['store_in_sqlite'] = True
            js.args.file = os.path.join(os.path.dirname(__file__), 'configs', 'main.yml')
            config_file = open(js.args.file, 'r')
            config_data = yaml.load(config_file)
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
            config_data = yaml.load(config_file)
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
            config_data = yaml.load(config_file)
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
            config_data = yaml.load(config_file)
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
            config_data = yaml.load(config_file)
            del (config_data['sqlite'][0]['store_in_sqlite'])
            del (config_data['sqlite'][0]['check_from_sqlite'])
            config_data['sqlite'][0]['compare'] = '0'
            js.chk_database(config_data, 'mock_pre', 'mock_post', check=True)

    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.login')
    @patch('jnpr.jsnapy.jsnapy.SnapAdmin.chk_database')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_get_hosts_1(self, mock_path, mock_chk, mock_login):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js = SnapAdmin()
        js.args.file = 'main.yml'
        js.get_hosts()
        mock_chk.assert_called()
        mock_login.assert_called()

    @patch('sys.exit')
    def test_get_hosts_2(self, mock_exit):
        js = SnapAdmin()
        js.args.file = 'main1.yml'
        js.args.check = True
        js.args.pre_snapfile = None
        with patch('jnpr.jsnapy.jsnapy.argparse.ArgumentParser.print_help') as mock_parser:
            js.get_hosts()
            mock_parser.assert_called()
            mock_exit.assert_called()

    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_get_hosts_3(self, mock_path):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js = SnapAdmin()
        js.args.snapcheck = False
        js.args.pre_snapfile = None
        js.args.file = 'no_such_file.yml'
        with self.assertRaises(SystemExit):
            js.get_hosts()

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
        js.get_hosts()
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
        js.get_hosts()
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
        js.get_hosts()
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
        js.get_hosts()
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

        js.get_hosts()
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

        js.get_hosts()
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

        js.get_hosts()
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

        js.get_hosts()
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

        js.get_hosts()
        self.assertFalse(mock_notify.called)
        self.assertFalse(mock_pass.called)
        self.assertTrue(mock_compare.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    def test_sqlite_parameters_1(self, mock_login, mock_arg):
        js = SnapAdmin()
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        js.args.snap = True
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snapfile = "mock_snap"
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    def test_sqlite_parameters_2(self, mock_login, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_2.yml')
        js.args.snap = True
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    def test_sqlite_parameters_3(self, mock_login, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_11.yml')
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        self.db['first_snap_id'] = 1
        self.db['second_snap_id'] = 0
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    def test_sqlite_parameters_4(self, mock_login, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_4.yml')
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        self.db['first_snap_id'] = 0
        self.db['second_snap_id'] = 1
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    def test_sqlite_parameters_5(self, mock_login, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
                                                                             diff=False, file=None, hostname=None,
                                                                             login=None, passwd=None, port=None,
                                                                             post_snapfile=None, pre_snapfile=None,
                                                                             snap=False, snapcheck=False,
                                                                             verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_5.yml')
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        self.db['first_snap_id'] = 0
        self.db['second_snap_id'] = 1
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    def test_sqlite_parameters_6(self, mock_login, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_2.yml')
        js.args.snap = False
        js.args.check = False
        js.args.snapcheck = True
        js.args.diff = False
        js.args.pre_snapfile = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    def test_sqlite_parameters_7(self, mock_login, mock_arg):
        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'main_1.yml')
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snapfile = "mock_snap"
        js.args.post_snapfile = "mock_snap2"
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_port_without_include(self, mock_connect):
        # this test case is for scenarios when devices are mentioned in the cfg file itself
        js = SnapAdmin()
        # js.args.snap = True
        js.args.hostname = None

        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_with_port.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        hosts = ['1.1.1.1']
        self.assertEqual(js.host_list, hosts)
        mock_connect.assert_called_with('1.1.1.1', 'abc', 'xyz', 'snap_1', port=44)

        # adding another device in the config dictionary
        # and checking the precedence b/w cmd and config params
        js.main_file['hosts'].append({'device': '1.1.1.15',
                                      'username': 'abc',
                                      'passwd': 'xyz',
                                      'port': 45})
        js.args.port = 100

        expected_calls_made = [call('1.1.1.1', 'abc', 'xyz', 'snap_1', port=100),
                               call('1.1.1.15', 'abc', 'xyz', 'snap_1', port=100)]
        js.login("snap_1")
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

        # deleting the port paramater from the config file and keeping the port param on cmd args
        for host in js.main_file['hosts']:
            if 'port' in host:
                del host['port']

        js.login("snap_1")
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

        # deleting the cmd line port param
        expected_calls_made = [call('1.1.1.1', 'abc', 'xyz', 'snap_1'),
                               call('1.1.1.15', 'abc', 'xyz', 'snap_1')]
        js.args.port = None
        js.login("snap_1")
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_port_with_include(self, mock_connect, mock_path):
        # this test case is for scenarios when devices are included using some other file
        js = SnapAdmin()
        js.args.snap = True
        js.args.hostname = None
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')

        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main2_with_port.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)

        hosts = ['1.1.1.3', '1.1.1.4', '1.1.1.5']
        expected_calls_made = [call('1.1.1.3', 'abc', 'def', 'snap_1', port=100),
                               call('1.1.1.4', 'abc', 'def', 'snap_1', port=101),
                               call('1.1.1.5', 'abc', 'def', 'snap_1', port=102)]

        js.login("snap_1")

        self.assertEqual(js.host_list, hosts)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)
        #    mock_connect.assert_called_with('1.1.1.1','abc','xyz','snap_1',port=44)


        # Adding the cmd-line port param and checking the precedence b/w cmd and config params
        js.args.port = 55
        expected_calls_made = [call('1.1.1.3', 'abc', 'def', 'snap_1', port=55),
                               call('1.1.1.4', 'abc', 'def', 'snap_1', port=55),
                               call('1.1.1.5', 'abc', 'def', 'snap_1', port=55)]
        js.login("snap_1")

        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

# with nested(
#     patch('sys.exit'),
#     patch('argparse.ArgumentParser.print_help'),
#     patch('logging.Logger'),
# ) as (mock_sys, mock_parser, mock_logger):
#     if __name__ == "__main__":
#         suite = unittest.TestLoader().loadTestsFromTestCase(TestSnapAdmin)
#         unittest.TextTestRunner(verbosity=2).run(suite)