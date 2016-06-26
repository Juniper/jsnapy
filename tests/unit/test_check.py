import unittest
import os
import yaml
from jnpr.jsnapy.check import Comparator
from mock import patch, MagicMock
import jnpr


class TestCheck(unittest.TestCase):

    def setUp(self):

        self.diff = False
        self.chk = False
        self.hostname = "10.216.193.114"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = "jbb.db"
        self.db['first_snap_id'] = None
        self.db['first_snap_id'] = None
        self.snap_del = False
        self.action = None

    @patch('logging.Logger.info')
    def test_no_test_file(self, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_incorrect_1.yml')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('logging.Logger.error') as mock_error:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                self.snap_del,
                "snap_is-equal_pre")
            err = "ERROR!! No test file found, Please mention test files !!"
            c_list = mock_error.call_args_list[0]
            self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('logging.Logger.info')
    def test_incorrect_test_file(self, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_incorrect_2.yml')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        filename = os.path.join('/etc', 'jsnapy', 'testfiles', "dummy.yml")
        with patch('logging.Logger.error') as mock_error:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                self.snap_del,
                "snap_is-equal_pre")
            err = "ERROR!! File %s not found" % filename
            c_list = mock_error.call_args_list[0]
            self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_incorrect_test_command(self, mock_path, mock_info):
        self.chk = False
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_incorrect_3.yml')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('logging.Logger.error') as mock_log:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                self.snap_del,
                "snap_is-equal_pre")
            err = "ERROR occurred, test keys 'command' or 'rpc' not defined properly"
            c_list = mock_log.call_args_list[0]
            print "c_list:",c_list
            self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('sys.exit')
    @patch('logging.Logger.info')
    def test_incorrect_test_format(self, mock_info, mock_sys):
        def fun():
            raise BaseException
        mock_sys.return_value = fun
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_incorrect_4.yml')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        self.db['check_from_sqlite'] = True
        with patch('logging.Logger.error') as mock_log:
            try:
                comp.generate_test_files(
                    main_file,
                    self.hostname,
                    self.chk,
                    self.diff,
                    self.db,
                    self.snap_del,
                    "snap_no-diff_pre",
                    self.action,
                    "snap_no-diff_post1")
            except BaseException:
                err = "ERROR!! Data stored in database is not in %s format"
                c_list = mock_log.call_args_list[0]
                self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_incorrect_test_format_2(self, mock_path, mock_info):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_incorrect_4.yml')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        with patch('logging.Logger.error') as mock_log:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                self.snap_del,
                "snap_no-diff_pre",
                self.action,
                "snap_no-diff_post1")
            err = "ERROR!! for checking snapshots in text format use '--diff' option"
            c_list = mock_log.call_args_list[0]
            print "c_list:", c_list
            self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_compare_xml(self, mock_path, mock_info):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_empty_test.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('jnpr.jsnapy.check.XmlComparator.xml_compare') as mock_compare:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                self.snap_del,
                "snap_no-diff_pre",
                self.action,
                "snap_no-diff_post")
            self.assertTrue(mock_compare.called)

    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_compare_diff(self, mock_path, mock_info):
        self.diff = True
        comp = Comparator()
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_empty_test.yml')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('jnpr.jsnapy.check.icdiff.diff') as mock_compare:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                self.snap_del,
                "snap_no-diff_pre",
                self.action,
                "snap_no-diff_post")
            self.assertTrue(mock_compare.called)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCheck)
    unittest.TextTestRunner(verbosity=2).run(suite)
