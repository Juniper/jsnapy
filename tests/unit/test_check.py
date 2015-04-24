import unittest
import os
import yaml
from jnpr.jsnap.check import Comparator
from mock import patch


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

    def test_no_test_file(self):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_incorrect_1.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('logging.Logger.info') as mock_log:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                "snap_is-equal_pre")
            err = "No test file, Please mention test files"
            c = mock_log.call_args_list[0]
            self.assertNotEqual(c[0][0].find(err), -1)

    @patch('logging.Logger.info')
    def test_incorrect_test_file(self, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_incorrect_2.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        filename = os.path.join(os.getcwd(), 'configs', "dummy.yml")
        with patch('logging.Logger.error') as mock_log:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                "snap_is-equal_pre")
            err = "File %s not found" % filename
            c = mock_log.call_args_list[0]
            self.assertNotEqual(c[0][0].find(err), -1)

    @patch('logging.Logger.info')
    def test_incorrect_test_command(self, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_incorrect_3.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('logging.Logger.error') as mock_log:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                "snap_is-equal_pre")
            err = "ERROR occurred, test keys 'command' or 'rpc' not defined properly"
            c = mock_log.call_args_list[0]
            self.assertNotEqual(c[0][0].find(err), -1)

    @patch('sys.exit')
    @patch('logging.Logger.info')
    def test_incorrect_test_format(self, mock_info, mock_sys):
        def fun():
            raise BaseException
        mock_sys.return_value = fun
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_incorrect_4.yml"
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
                    "snap_no-diff_pre",
                    "snap_no-diff_post1")

            except BaseException:
                err = "ERROR!! Data stored in database is not in %s format"
                c = mock_log.call_args_list[0]
                self.assertNotEqual(c[0][0].find(err), -1)

    @patch('logging.Logger.info')
    def test_incorrect_test_format_2(self, mock_info):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_incorrect_4.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('logging.Logger.error') as mock_log:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                "snap_no-diff_pre",
                "snap_no-diff_post1")

            err = "ERROR!! for checking snapshots in text format use '--diff' option"
            c = mock_log.call_args_list[0]
            self.assertNotEqual(c[0][0].find(err), -1)

    @patch('logging.Logger.info')
    def test_compare_xml(self, mock_info):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_empty_test.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('jnpr.jsnap.check.XmlComparator.xml_compare') as mock:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                "snap_no-diff_pre",
                "snap_no-diff_post")
            self.assertTrue(mock.called)

    @patch('logging.Logger.info')
    def test_compare_diff(self, mock_info):
        self.diff = True
        comp = Comparator()
        conf_file = "configs/main_empty_test.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        with patch('jnpr.jsnap.snap_diff.Diff.diff_files') as mock:
            comp.generate_test_files(
                main_file,
                self.hostname,
                self.chk,
                self.diff,
                self.db,
                "snap_no-diff_pre",
                "snap_no-diff_post")
            self.assertTrue(mock.called)

suite = unittest.TestSuite()
suite.addTest(TestCheck("test_no_test_file"))
suite.addTest(TestCheck("test_compare_xml"))
suite.addTest(TestCheck("test_incorrect_test_file"))
suite.addTest(TestCheck("test_incorrect_test_command"))
suite.addTest(TestCheck("test_incorrect_test_format"))
suite.addTest(TestCheck("test_incorrect_test_format_2"))
suite.addTest(TestCheck("test_compare_diff"))

unittest.TextTestRunner().run(suite)
