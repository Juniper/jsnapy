import unittest
import yaml
import os
from jnpr.jsnapy.jsnapy import SnapAdmin
from mock import patch, MagicMock
from contextlib import nested
from nose.plugins.attrib import attr
import argparse

@attr('unit')
class TestSnapAdmin(unittest.TestCase):

    def setUp(self):
        self.diff = False
        self.hostname = "10.216.193.114"
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
            "10.216.193.114",
            js.main_file)
        self.assertTrue(mock_parse.called)

    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_hostname(self, mock_connect ):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_1.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        hosts = ['10.216.193.114']
        self.assertEqual(js.host_list, hosts)


    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_multiple_hostname(self, mock_path, mock_connect, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main1.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        hosts = ['10.209.16.203', '10.209.16.204', '10.209.16.205']
        self.assertEqual(js.host_list, hosts)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_connect_snap(self, mock_log, mock_gen_reply, mock_dev, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

        js = SnapAdmin()
        js.args.file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_1.yml')
        js.args.snap = True
        js.args.pre_snapfile = "mock_snap"
        js.get_hosts()
        self.assertTrue(mock_gen_reply.called)
        self.assertTrue(mock_dev.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    def test_connect_check(self, mock_compare, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            '10.216.193.114',
            config_data,
            js.args.pre_snapfile,
            None,
            None)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.Device')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('jnpr.jsnapy.SnapAdmin.generate_rpc_reply')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_connect_snapcheck(
            self, mock_log, mock_snap, mock_check, mock_dev, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            '10.216.193.114',
            config_data,
            js.args.pre_snapfile,
            None,
            None)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    def test_connect_diff(self, mock_compare, arg_exit):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            '10.216.193.114',
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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnapy.notify.Notification.notify')
    @patch('jnpr.jsnapy.jsnapy.get_path')
    def test_check_mail(self, mock_path, mock_notify, mock_pass, mock_compare, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
        mock_compare.return_value = MagicMock(result = 'Failed')
        
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
        mock_compare.return_value = MagicMock(result = 'Failed')
        
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
        mock_compare.return_value = MagicMock(result = 'Passed')
        
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
        mock_compare.return_value = MagicMock(result = 'Failed')
        
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
        mock_compare.return_value = MagicMock(result = 'Failed')
        
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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

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

with nested(
    patch('sys.exit'),
    patch('argparse.ArgumentParser.print_help'),
    patch('logging.Logger'),
) as (mock_sys, mock_parser, mock_logger):
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSnapAdmin)
        unittest.TextTestRunner(verbosity=2).run(suite)
