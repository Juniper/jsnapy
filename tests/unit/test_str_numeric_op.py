import unittest
import yaml
from jnpr.jsnapy.check import Comparator
from mock import patch
import os
from nose.plugins.attrib import attr
@attr('unit')
class TestStrNumericOperators(unittest.TestCase):

    def setUp(self):

        self.diff = False
        self.hostname = "1.1.1.1"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""
        self.snap_del = False
        self.action = None

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_all_same_equal_fail(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_all-same-equal-fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_all_same_fail(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_all-same-fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_all_same_success(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_all-same-success.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_all_same_ignore_null_1(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_all-same-ignore-null_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_all_same_ignore_null_2(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_all-same-ignore-null_2.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_all_same_ignore_null_3(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_all-same-ignore-null_3.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0) #comparison between None values. All values are None.   
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_all_same_ignore_null_4(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_all-same-ignore-null_4.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_all_same_ignore_null_pass(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_all-same-ignore-null_pass.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_all-same-success_pre_ignore_null")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 2)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_equal_success(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-equal-item.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_equal_fail(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-equal.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_equal_fail_ignore_null_1(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-equal_ignore-null_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_equal_fail_ignore_null_2(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-equal_ignore-null_2.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_failed, 0)
    
    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_equal_fail_ignore_null_3(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-equal_ignore-null_3.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_equal_fail_ignore_null_4(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-equal_ignore-null_4.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_equal_success_ignore_null_1(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-equal_ignore-null_5.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-equal_pre_special")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    
    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_is_equal_success_ignore_null_2(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-equal_ignore-null_6.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-equal_pre_special")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)


    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_equal(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-equal.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_equal_fail(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-equal.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_equal_ignore_null_1(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-equal_ignore-null_1.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_equal_ignore_null_2(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-equal_ignore-null_2.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)
    
    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_equal_ignore_null_3(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-equal_ignore-null_3.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_equal_ignore_null_4(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-equal_ignore-null_4.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_equal_ignore_null_5(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-equal_ignore-null_5.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_is-equal_pre_special")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_exists_pass(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-exists.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_exists_ignore_null_fail(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-exists_ignore-null_fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_exists_ignore_null_skip(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-exists_ignore-null.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        # print main_file
        oper = comp.generate_test_files(
            main_file,
            self.hostname,
            self.chk,
            self.diff,
            self.db,
            self.snap_del,
            "snap_not-exists_pre")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_not_exists_fail(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-exists_fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_exists(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_exists.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_exists_ignore_null_fail(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_exists_ignore-null_fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_exists_ignore_null_skip(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_exists_ignore-null_skip.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 0)

    @patch('logging.Logger.debug')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.check.get_path')
    def test_exists_fail(self, mock_path, mock_debug, mock_info):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_exists.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
