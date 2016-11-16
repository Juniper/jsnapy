import unittest
import yaml
import os
from jnpr.jsnapy.jsnapy import SnapAdmin
from mock import patch, MagicMock, call
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
                                 'configs', 'main_6.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        expected_calls_made = [call('10.216.193.114','abc','xyz','snap_1'),
                                call('10.216.193.115','abc','xyz','snap_1'), 
                                call('10.216.193.116','abc','xyz','snap_1'),
                                ]  
        
        hosts = ['10.216.193.114','10.216.193.115','10.216.193.116']
        self.assertEqual(js.host_list, hosts)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)
        


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

        #extending the test to check for device overlap among groups
        js.main_file['hosts'][0]['group']='MX, EX'
        expected_calls_made = [call('10.209.16.203','abc','def','snap_1'),
                                call('10.209.16.204','abc','def','snap_1'), 
                                call('10.209.16.205','abc','def','snap_1'),
                                call('10.209.16.206','abc','def','snap_1'),
                                call('10.209.16.212','abc','def','snap_1'),
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
        #we check whether get_test was called, indirectly checking whether compare_tests was called.
        mock_check.assert_called_once_with(
            '10.216.193.114',
            config_data,
            "mock_snap",
            None,
            None) 
    

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
        #we check whether get_test was called, indirectly checking whether compare_tests was called.
        expected_calls_made = [call('10.216.193.114',config_data,'PRE',None, None),
                                call('10.216.193.114',config_data,'PRE_42',None, None),
                                call('10.216.193.114',config_data,'PRE_314',None, None)
                                ]  
        mock_check.assert_has_calls(expected_calls_made, any_order=True)


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
        mock_compare.return_value = MagicMock(result = 'Passed')
        
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
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_port_without_include(self,mock_connect):
        #this test case is for scenarios when devices are mentioned in the cfg file itself
        js = SnapAdmin()
        # js.args.snap = True  
        js.args.hostname = None

        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_with_port.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        hosts = ['10.216.193.114']
        self.assertEqual(js.host_list, hosts)
        mock_connect.assert_called_with('10.216.193.114','abc','xyz','snap_1',port=44)
        
        #adding another device in the config dictionary 
        #and checking the precedence b/w cmd and config params
        js.main_file['hosts'].append({'device':'10.216.193.115',
                                    'username':'abc',
                                    'passwd':'xyz',
                                    'port':45})
        js.args.port=100
        
        
        expected_calls_made = [call('10.216.193.114','abc','xyz','snap_1',port=100),
                                call('10.216.193.115','abc','xyz','snap_1',port=100)]   
        js.login("snap_1")
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)
        
        #deleting the port paramater from the config file and keeping the port param on cmd args
        for host in js.main_file['hosts']: 
            if 'port' in host:
                del host['port']
           
        js.login("snap_1")
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)
        
        #deleting the cmd line port param
        expected_calls_made = [call('10.216.193.114','abc','xyz','snap_1'),
                                call('10.216.193.115','abc','xyz','snap_1')]   
        js.args.port=None
        js.login("snap_1")
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

   
    @patch('jnpr.jsnapy.jsnapy.get_path')
    @patch('jnpr.jsnapy.SnapAdmin.connect')
    def test_port_with_include(self,mock_connect,mock_path):
        #this test case is for scenarios when devices are included using some other file
        js = SnapAdmin()
        js.args.snap = True  
        js.args.hostname = None
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')

        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main2_with_port.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        
        hosts = ['10.209.16.203','10.209.16.204','10.209.16.205']
        expected_calls_made = [call('10.209.16.203','abc','def','snap_1',port=100),
                                call('10.209.16.204','abc','def','snap_1',port=101), 
                                call('10.209.16.205','abc','def','snap_1',port=102)] 
        
        js.login("snap_1")
        
        self.assertEqual(js.host_list, hosts)
        mock_connect.assert_has_calls(expected_calls_made, any_order=True)
        #    mock_connect.assert_called_with('10.216.193.114','abc','xyz','snap_1',port=44)
        
        
        #Adding the cmd-line port param and checking the precedence b/w cmd and config params
        js.args.port=55
        expected_calls_made = [call('10.209.16.203','abc','def','snap_1',port=55),
                                call('10.209.16.204','abc','def','snap_1',port=55), 
                                call('10.209.16.205','abc','def','snap_1',port=55)]   
        js.login("snap_1")

        mock_connect.assert_has_calls(expected_calls_made, any_order=True)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_test_file_1(self, mock_log, mock_login, mock_sys, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snap = False
        js.args.file = None
        js.args.test_file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'test_diff.yml')
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.login = "regress"
        js.args.hostname = "10.221.130.68"
        js.args.passwd = "MaRtInI"
        js.args.post_snapfile = "mock_snap2"
        js.args.pre_snapfile = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            js.get_hosts()
            self.assertTrue(js.args.file)
        
    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_test_file_2(self, mock_log, mock_login, mock_sys, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snap = True
        js.args.file = None
        js.args.test_file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'test_diff.yml')
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = False
        js.args.login = "regress"
        js.args.hostname = "10.221.130.68"
        js.args.passwd = "MaRtInI"
        js.args.post_snapfile = None
        js.args.pre_snapfile = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            js.get_hosts()
            self.assertTrue(js.args.file)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.SnapAdmin.login')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_test_file_3(self, mock_log, mock_login, mock_sys, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snap = False
        js.args.file = None
        js.args.test_file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'test_diff.yml')
        js.args.check = False
        js.args.snapcheck = True
        js.args.diff = False
        js.args.login = "regress"
        js.args.hostname = "10.221.130.68"
        js.args.passwd = "MaRtInI"
        js.args.post_snapfile = "mock_snap2"
        js.args.pre_snapfile = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            js.get_hosts()
            self.assertTrue(js.args.file)        


    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.get_hosts')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_test_file_4(self, mock_log,mock_sys, mock_get_hosts, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snap = False
        js.args.file = None
        js.args.test_file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'test_diff.yml')
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = True
        js.args.login = "regress"
        js.args.hostname = "10.221.130.68"
        js.args.passwd = "MaRtInI"
        js.args.post_snapfile = "mock_snap2"
        js.args.pre_snapfile = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            self.assertFalse(mock_get_hosts.called)

    @patch('argparse.ArgumentParser.exit')
    @patch('jnpr.jsnapy.SnapAdmin.get_hosts')
    @patch('jnpr.jsnapy.jsnapy.sys.exit')
    @patch('jnpr.jsnapy.jsnapy.logging.getLogger')
    def test_check_arguments_test_file_5(self, mock_log, mock_sys, mock_get_hosts, mock_arg):
        argparse.ArgumentParser.parse_args = MagicMock()
        argparse.ArgumentParser.parse_args.return_value = argparse.Namespace(check=False,
            diff=False, file=None, hostname=None, login=None, passwd=None, port=None, post_snapfile=None, pre_snapfile=None, snap=False, snapcheck=False, verbosity=None, version=False)

        js = SnapAdmin()
        js.args.snap = False
        js.args.file = None
        js.args.test_file = os.path.join(os.path.dirname(__file__),
                                    'configs', 'test_diff.yml')
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.login = None
        js.args.hostname = "10.221.130.68"
        js.args.passwd = "MaRtInI"
        js.args.post_snapfile = "mock_snap2"
        js.args.pre_snapfile = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            self.assertFalse(mock_get_hosts.called)
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()

with nested(
    patch('sys.exit'),
    patch('argparse.ArgumentParser.print_help'),
    patch('logging.Logger'),
) as (mock_sys, mock_parser, mock_logger):
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSnapAdmin)
        unittest.TextTestRunner(verbosity=2).run(suite)
