import unittest
import yaml
from jnpr.jsnapy.check import Comparator
from mock import patch


class TestStrNumericOperators(unittest.TestCase):

    def setUp(self):

        self.diff = False
        self.hostname = "10.216.193.114"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""
        self.snap_del = False
        self.action = None

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_all_same_equal_fail(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_all-same-equal-fail.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_all-same-equal-fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_all_same_fail(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_all-same-fail.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_all-same-fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_all_same_success(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_all-same-success.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_all-same-success_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_is_equal_success(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_is-equal-item.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-equal-item_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_is_equal_fail(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_is-equal.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-equal_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_not_equal(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_not-equal.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_not-equal_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_not_equal_fail(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_not-equal.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_not-equal_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_not_exists_pass(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_not-exists.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_not-exists_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_not_exists_fail(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_not-exists_fail.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_not-exists_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_exists(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_exists.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_exists_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    def test_exists_fail(self, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_exists.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_exists_fail_pre")

        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestStrNumericOperators)
    unittest.TextTestRunner(verbosity=2).run(suite)
