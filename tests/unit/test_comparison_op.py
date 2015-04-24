import unittest
import yaml
from jnpr.jsnap.check import Comparator
from mock import patch


class TestComparisonOperator(unittest.TestCase):

    def setUp(self):

        self.diff = False
        self.hostname = "10.216.193.114"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = "jbb.db"
        self.db['first_snap_id'] = None
        self.db['first_snap_id'] = None

    def test_no_diff(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_no-diff.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_no-diff_pre",
            "snap_no-diff_post")

        self.assertEqual(ab.no_passed, 2)
        self.assertEqual(ab.no_failed, 4)

    def test_list_not_less_fail(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_list-not-less.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_no-diff_pre",
            "snap_no-diff_post")

        self.assertEqual(ab.no_passed, 1)
        self.assertEqual(ab.no_failed, 1)

    def test_list_not_more_fail(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_list-not-more.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_no-diff_pre",
            "snap_no-diff_post")

        self.assertEqual(ab.no_passed, 1)
        self.assertEqual(ab.no_failed, 1)

    def test_list_not_less_pass(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_list-not-less.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_no-diff_pre",
            "snap_3")

        self.assertEqual(ab.no_passed, 2)
        self.assertEqual(ab.no_failed, 0)

    def test_list_not_more_pass(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_list-not-more.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_no-diff_pre",
            "snap_3")

        self.assertEqual(ab.no_passed, 2)
        self.assertEqual(ab.no_failed, 0)

    def test_delta(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_delta.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_delta_pre",
            "snap_delta_post")

        self.assertEqual(ab.no_passed, 1)
        self.assertEqual(ab.no_failed, 0)

    def test_delta_fail(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_delta.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_delta_fail_pre",
            "snap_delta_fail_post")

        self.assertEqual(ab.no_passed, 0)
        self.assertEqual(ab.no_failed, 1)

    def test_no_diff_2(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_dot-dot.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_no-diff_pre",
            "snap_no-diff_post")

        self.assertEqual(ab.no_passed, 1)
        self.assertEqual(ab.no_failed, 5)

    def test_no_diff_2_pass(self):
        self.chk = True
        comp = Comparator()
        conf_file = "configs/main_dot-dot.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_no-diff_pre",
            "snap_3")

        self.assertEqual(ab.no_passed, 6)
        self.assertEqual(ab.no_failed, 0)

    def test_no_diff_pass(self):
        self.chk = True
        self.db['check_from_sqlite'] = True
        comp = Comparator()
        conf_file = "configs/main_no-diff_sql.yml"
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)

        ab = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            "snap_no-diff_pre",
            "snap_no-diff_post1")

        self.assertEqual(ab.no_passed, 6)
        self.assertEqual(ab.no_failed, 0)

with patch('logging.Logger') as mock:
    suite = unittest.TestSuite()
    suite.addTest(TestComparisonOperator("test_no_diff"))
    suite.addTest(TestComparisonOperator("test_delta"))
    suite.addTest(TestComparisonOperator("test_delta_fail"))
    suite.addTest(TestComparisonOperator("test_no_diff_2"))
    suite.addTest(TestComparisonOperator("test_no_diff_pass"))
    suite.addTest(TestComparisonOperator("test_no_diff_2_pass"))
    suite.addTest(TestComparisonOperator("test_list_not_less_fail"))
    suite.addTest(TestComparisonOperator("test_list_not_more_fail"))
    suite.addTest(TestComparisonOperator("test_list_not_less_pass"))
    suite.addTest(TestComparisonOperator("test_list_not_more_pass"))
    unittest.TextTestRunner().run(suite)
