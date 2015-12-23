import unittest
import sys
import yaml
from jnpr.jsnapy.check import Comparator
from mock import patch

class TestStringOperators(unittest.TestCase):

    def setUp(self):
        self.diff = False
        self.hostname = "10.216.193.114"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""

    def test_contains(self):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_contains.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_contains_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    def test_contains_fail(self):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_contains.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_contains_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    def test_is_in(self):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_is-in.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_is-in_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    def test_is_in_fail(self):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_is-in.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_is-in_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    def test_not_in(self):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_not-in.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_not-in_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    def test_not_in_pass(self):
        self.chk = False
        comp = Comparator()
        conf_file = "configs/main_not-in.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_not-in_fail_pre")

        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

with patch('logging.Logger') as mock_logger:
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(TestStringOperators)
        unittest.TextTestRunner(verbosity=2).run(suite)

