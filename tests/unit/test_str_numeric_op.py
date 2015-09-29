import unittest
import sys
import yaml
from jnpr.jsnap.check import Comparator
from cStringIO import StringIO
from mock import patch


class TestStrNumericOperators(unittest.TestCase):

    def setUp(self):

        self.diff = False
        self.hostname = "10.216.193.114"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""

    def test_all_same_equal_fail(self):
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
            "snap_all-same-equal-fail_pre")

        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    def test_all_same_fail(self):
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
            "snap_all-same-fail_pre")

        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    def test_all_same_success(self):
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
            "snap_all-same-success_pre")

        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    def test_is_equal_success(self):
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
            "snap_is-equal-item_pre")

        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    def test_is_equal_fail(self):
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
            "snap_is-equal_pre")

        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    def test_not_equal(self):
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
            "snap_not-equal_pre")

        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    def test_not_equal_fail(self):
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
            "snap_not-equal_fail_pre")

        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    def test_not_exists_pass(self):
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
            "snap_not-exists_pre")

        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    def test_not_exists_fail(self):
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
            "snap_not-exists_pre")

        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    def test_exists(self):
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
            "snap_exists_pre")

        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    def test_exists_fail(self):
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
            "snap_exists_fail_pre")

        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

with patch('logging.Logger') as mock_logger:
    suite = unittest.TestSuite()
    suite.addTest(TestStrNumericOperators("test_all_same_equal_fail"))
    suite.addTest(TestStrNumericOperators("test_all_same_fail"))
    suite.addTest(TestStrNumericOperators("test_all_same_success"))
    suite.addTest(TestStrNumericOperators("test_is_equal_success"))
    suite.addTest(TestStrNumericOperators("test_is_equal_fail"))
    suite.addTest(TestStrNumericOperators("test_not_equal"))
    suite.addTest(TestStrNumericOperators("test_not_equal_fail"))
    suite.addTest(TestStrNumericOperators("test_not_exists_pass"))
    suite.addTest(TestStrNumericOperators("test_not_exists_fail"))
    suite.addTest(TestStrNumericOperators("test_exists"))
    suite.addTest(TestStrNumericOperators("test_exists_fail"))
    unittest.TextTestRunner().run(suite)
