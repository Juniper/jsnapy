import unittest
import yaml
from jnpr.jsnapy.check import Comparator
from unittest.mock import patch
import os
import nose2

class TestStringOperators(unittest.TestCase):

    def setUp(self):
        self.diff = False
        self.hostname = "1.1.1.1"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""
        self.snap_del = False

    @patch('jnpr.jsnapy.check.get_path')
    def test_contains(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_contains.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_contains_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_contains_fail(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_contains.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_contains_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    
    @patch('jnpr.jsnapy.check.get_path')
    def test_contains_ignore_null_fail(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_contains_ignore-null_fail.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_contains_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_contains_ignore_null_fail_1(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_contains_ignore-null_fail_1.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_contains_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_contains_ignore_null_skip(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_contains_ignore-null_skip.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_contains_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_contains_ignore_null_skip_1(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_contains_ignore-null_skip_1.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_contains_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_contains_ignore_null_pass(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_contains_ignore-null_pass.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_contains_pre_ignore_null")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_is_in(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-in.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-in_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_is_in_fail(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-in.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-in_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_in_ignore_null_fail(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-in_ignore-null_fail.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-in_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_in_ignore_null_fail_1(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-in_ignore-null_fail_1.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-in_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_is_in_ignore_null_skip(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-in_ignore-null_skip.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-in_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_in_ignore_null_skip_1(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-in_ignore-null_skip_1.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-in_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_in_ignore_null_pass(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-in_ignore-null_pass.yml')
        config_file = open(conf_file, 'r')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        main_file = yaml.load(config_file, Loader=yaml.FullLoader)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-in_pre_ignore_null")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 2)

    @patch('jnpr.jsnapy.check.get_path')
    def test_not_in_pass(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-in.yml')
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
            "snap_not-in_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_not_in_ignore_null_fail(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-in_ignore-null_fail.yml')
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
            "snap_not-in_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_not_in_ignore_null_fail_1(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-in_ignore-null_fail_1.yml')
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
            "snap_not-in_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_not_in_ignore_null_skip(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-in_ignore-null_skip.yml')
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
            "snap_not-in_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_not_in_ignore_null_skip_1(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-in_ignore-null_skip_1.yml')
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
            "snap_not-in_pre")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_in_ignore_null_pass(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-in_ignore-null_pass.yml')
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
            "snap_not-in_pre_ignore_null")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_not_in(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-in.yml')
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
            "snap_not-in_fail_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

with patch('logging.Logger') as mock_logger:
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(
            TestStringOperators)
        unittest.TextTestRunner(verbosity=2).run(suite)
