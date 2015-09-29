import unittest
import yaml
from jnpr.jsnap.jsnap import Jsnap
from mock import patch
from contextlib import nested


class TestJsnap(unittest.TestCase):

    def setUp(self):

        self.diff = False
        self.hostname = "10.216.193.114"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""
        self.db['first_snap_id'] = None
        self.db['second_snap_id'] = None

    @patch('jnpr.jsnap.jsnap.Parse')
    def test_snap(self, mock_parse):
        js = Jsnap()
        conf_file = "configs/main.yml"
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.generate_rpc_reply("10.216.193.114", "snap_mock", "username")
        self.assertTrue(mock_parse.called)

    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_sqlite_parameters_1(self, mock_login):
        js = Jsnap()
        js.args.file = "configs/main_1.yml"
        js.args.snap = True
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_sqlite_parameters_2(self, mock_login):
        js = Jsnap()
        js.args.file = "configs/main_2.yml"
        js.args.snap = True
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snap_file = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_sqlite_parameters_3(self, mock_login):
        js = Jsnap()
        js.args.file = "configs/main_3.yml"
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snap_file = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_sqlite_parameters_4(self, mock_login):
        js = Jsnap()
        js.args.file = "configs/main_4.yml"
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snap_file = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        self.db['first_snap_id'] = 0
        self.db['second_snap_id'] = 1
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_sqlite_parameters_5(self, mock_login):
        js = Jsnap()
        js.args.file = "configs/main_5.yml"
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snap_file = "mock_snap"
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        self.db['first_snap_id'] = 0
        self.db['second_snap_id'] = 1
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_sqlite_parameters_6(self, mock_login):
        js = Jsnap()
        js.args.file = "configs/main_2.yml"
        js.args.snap = False
        js.args.check = False
        js.args.snapcheck = True
        js.args.diff = False
        js.args.pre_snap_file = "mock_snap"
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = 'jbb.db'
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_sqlite_parameters_7(self, mock_login):
        js = Jsnap()
        js.args.file = "configs/main_1.yml"
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        self.assertEqual(js.db, self.db)

    @patch('jnpr.jsnap.jsnap.Jsnap.connect')
    def test_hostname(self, mock_connect):
        js = Jsnap()
        conf_file = "configs/main_1.yml"
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        hosts = ['10.216.193.114']
        self.assertEqual(js.host_list, hosts)

    @patch('jnpr.jsnap.jsnap.Jsnap.connect')
    def test_multiple_hostname(self, mock_connect):
        js = Jsnap()
        conf_file = "configs/main1.yml"
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        js.login("snap_1")
        hosts = ['10.209.16.203', '10.209.16.204', '10.209.16.205']
        self.assertEqual(js.host_list, hosts)

    @patch('jnpr.jsnap.jsnap.Device')
    @patch('jnpr.jsnap.jsnap.Jsnap.generate_rpc_reply')
    def test_connect_snap(self, mock_gen_reply, mock_dev):
        js = Jsnap()
        js.args.file = "configs/main_1.yml"
        js.args.snap = True
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        self.assertTrue(mock_gen_reply.called)
        self.assertTrue(mock_dev.called)

    @patch('jnpr.jsnap.jsnap.Jsnap.compare_tests')
    def test_connect_check(self, mock_compare):
        js = Jsnap()
        js.args.file = "configs/main_1.yml"
        js.args.check = True
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        mock_compare.assert_called_once_with('10.216.193.114')

    @patch('jnpr.jsnap.jsnap.Device')
    @patch('jnpr.jsnap.jsnap.Jsnap.compare_tests')
    @patch('jnpr.jsnap.jsnap.Jsnap.generate_rpc_reply')
    def test_connect_snapcheck(self, mock_snap, mock_check, mock_dev):
        js = Jsnap()
        js.args.file = "configs/main_1.yml"
        js.args.snapcheck = True
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        self.assertTrue(mock_snap.called)
        self.assertTrue(mock_dev.called)
        mock_check.assert_called_once_with('10.216.193.114')

    @patch('jnpr.jsnap.jsnap.Jsnap.compare_tests')
    def test_connect_diff(self, mock_compare):
        js = Jsnap()
        js.args.file = "configs/main_1.yml"
        js.args.diff = True
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        mock_compare.assert_called_once_with('10.216.193.114')

    @patch('sys.exit')
    def test_check_arguments_1(self, mock_sys):
        js = Jsnap()
        js.args.snap = False
        js.args.check = True
        js.args.snapcheck = False
        js.args.diff = False
        js.args.pre_snap_file = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()

    @patch('sys.exit')
    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_check_arguments_2(self, mock_login, mock_sys):
        js = Jsnap()
        js.args.snap = False
        js.args.file = "configs/main_3.yml"
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

    @patch('sys.exit')
    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_check_arguments_3(self, mock_login, mock_sys):
        js = Jsnap()
        js.args.snap = False
        js.args.file = "configs/main_3.yml"
        js.args.check = False
        js.args.snapcheck = True
        js.args.diff = False
        js.args.post_snapfile = "mock_snap_2"
        js.args.pre_snapfile = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            js.get_hosts()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()

    @patch('sys.exit')
    @patch('jnpr.jsnap.jsnap.Jsnap.login')
    def test_check_arguments_4(self, mock_login, mock_sys):
        js = Jsnap()
        js.args.snap = False
        js.args.file = "configs/main_3.yml"
        js.args.check = False
        js.args.snapcheck = False
        js.args.diff = True
        js.args.post_snapfile = None
        js.args.pre_snapfile = "mock_snap"
        with patch('argparse.ArgumentParser.print_help') as mock_parser:
            js.check_arguments()
            js.get_hosts()
            mock_sys.assert_called_with(1)
            mock_parser.assert_called_with()

    @patch('jnpr.jsnap.jsnap.Jsnap.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnap.jsnap.Notification.notify')
    def test_check_mail(self, mock_notify, mock_pass, mock_compare):
        js = Jsnap()
        js.args.file = "configs/main_mail.yml"
        js.args.check = True
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        self.assertTrue(mock_notify.called)

    @patch('jnpr.jsnap.jsnap.Device')
    @patch('jnpr.jsnap.jsnap.Jsnap.generate_rpc_reply')
    @patch('jnpr.jsnap.jsnap.Jsnap.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnap.jsnap.Notification.notify')
    def test_snapcheck_mail(
            self, mock_notify, mock_pass, mock_compare, mock_reply, mock_dev):
        js = Jsnap()
        js.args.file = "configs/main_mail.yml"
        js.args.snapcheck = True
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        self.assertTrue(mock_notify.called)

    @patch('jnpr.jsnap.jsnap.Jsnap.generate_rpc_reply')
    @patch('jnpr.jsnap.jsnap.Device')
    @patch('jnpr.jsnap.jsnap.Notification.notify')
    def test_snap_mail(self, mock_notify, mock_pass, mock_compare):
        js = Jsnap()
        js.args.file = "configs/main_mail.yml"
        js.args.snap = True
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        self.assertFalse(mock_notify.called)

    @patch('jnpr.jsnap.jsnap.Jsnap.compare_tests')
    @patch('getpass.getpass')
    @patch('jnpr.jsnap.jsnap.Notification.notify')
    def test_check_mail_password(self, mock_notify, mock_pass, mock_compare):
        js = Jsnap()
        js.args.file = "configs/main_mail_2.yml"
        js.args.check = True
        js.args.pre_snap_file = "mock_snap"
        js.get_hosts()
        self.assertTrue(mock_notify.called)
        self.assertTrue(mock_pass.called)


with nested(
    patch('sys.exit'),
    patch('argparse.ArgumentParser.print_help'),
    patch('logging.Logger')
) as (mock_sys, mock_parser, mock_logger):
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(TestJsnap)
        unittest.TextTestRunner(verbosity=2).run(suite)
