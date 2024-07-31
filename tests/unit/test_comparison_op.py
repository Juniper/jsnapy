import unittest
import yaml
from jnpr.jsnapy.check import Comparator
from unittest.mock import patch
import nose2
import os


class TestComparisonOperator(unittest.TestCase):

    def setUp(self):

        self.diff = False
        self.hostname = "1.1.1.1"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = "jbb.db"
        self.db['first_snap_id'] = None
        self.db['first_snap_id'] = None
        self.snap_del = False
        self.action = None

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_fail(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 1)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_ignore_null_fail(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less_ignore-null_fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 2)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_ignore_null_fail_1(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less_ignore-null_fail_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 1)#null case will pass
        self.assertEqual(oper.no_failed, 1)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_ignore_null_skip(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less_ignore-null_skip.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_ignore_null_skip_1(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less_ignore-null_skip_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 1) # even if no nodes is found, comparison between null and null passes
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_ignore_null_true_1(self, mock_path):
        # Test to check if xml element not present in first snapshot and if ignore-NULL
        # flag is set, it should ignore the test and move ahead.
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less_ignore-null_skip_2.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_exists_pre",
            self.action,
            "snap_exists_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_ignore_null_true_2(self, mock_path):
        #Test to check if xml element is present in first snapshot but not present in second snapshot and if ignore-NULL
        #flag is set, it should return failure in the test
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less_ignore-null_skip_2.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_exists_post",
            self.action,
            "snap_exists_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_ignore_null_id_skip(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less_ignore-null_id_skip.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_less_pass(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-less.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_3")
        self.assertEqual(oper.no_passed, 2)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_fail(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-more.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_pass(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-more.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_3")
        self.assertEqual(oper.no_passed, 2)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_ignore_null_fail(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-more_ignore-null_fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_3")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 2)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_ignore_null_fail_1(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-more_ignore-null_fail_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_3")
        self.assertEqual(oper.no_passed, 2)#the name is kinda misleading but in line with the convention    
        self.assertEqual(oper.no_failed, 0)
 
    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_ignore_null_skip(self, mock_path):
        #     Test to check if xml element not present in second snapshot if ignore-NULL
        #     flag is set, it should ignore the test and move ahead.
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-more_ignore-null_skip.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_3")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_ignore_null_skip_2(self, mock_path):
        #Test to check if xml element present in second snapshot but not present in second snapshot and if ignore-NULL
        #flag is set, it should return failure.
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-more_ignore-null_skip_2.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_exists_pre",
            self.action,
            "snap_exists_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_ignore_null_skip_1(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-more_ignore-null_skip_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_3")
        self.assertEqual(oper.no_passed, 2)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_ignore_null_id_skip(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list-not-more_ignore-null_id_skip.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_3")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_delta(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_delta_pre",
            self.action,
            "snap_delta_post")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_ignore_null_fail(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta_ignore-null_fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_delta_pre",
            self.action,
            "snap_delta_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)
    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_ignore_null_fail_1(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta_ignore-null_fail_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_delta_pre",
            self.action,
            "snap_delta_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_ignore_null_skip(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta_ignore-null_skip.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_delta_pre",
            self.action,
            "snap_delta_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_ignore_null_skip_1(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta_ignore-null_skip_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_delta_pre",
            self.action,
            "snap_delta_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_ignore_null_id_skip(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta_ignore-null_id_skip.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_delta_pre",
            self.action,
            "snap_delta_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_empty_id(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta_empty_id.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_delta_pre",
            self.action,
            "snap_delta_post")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_fail(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_delta_fail_pre",
            self.action,
            "snap_delta_fail_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_no_diff(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_no-diff.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 2)
        self.assertEqual(oper.no_failed, 4)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_no_diff_2(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_dot-dot.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 6)

    @patch('jnpr.jsnapy.check.get_path')
    @patch('jnpr.jsnapy.sqlite_get.get_path')
    def test_no_diff_2_pass(self, mock_sqlite_path, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_dot-dot.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_sqlite_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_3")
        self.assertEqual(oper.no_passed, 6)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    @patch('jnpr.jsnapy.sqlite_get.get_path')
    def test_no_diff_pass(self, sqlite_mock_path, mock_path):
        self.hostname = '10.216.193.114'
        self.chk = True
        self.db['check_from_sqlite'] = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_no-diff_sql.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        sqlite_mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')

        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post1")
        self.assertEqual(oper.no_passed, 6)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_no_diff_ignore_null_id_skip(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_no-diff_ignore-null_id_skip.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_no-diff_pre",
            self.action,
            "snap_no-diff_post")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

with patch('logging.Logger') as mock_logger:
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(
            TestComparisonOperator)
        unittest.TextTestRunner(verbosity=2).run(suite)
