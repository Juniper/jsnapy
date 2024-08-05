import unittest
import os
import yaml
from jnpr.jsnapy.check import Comparator
from jnpr.jsnapy.operator import Operator
from unittest.mock import patch, MagicMock
import nose2
from lxml import etree

class TestCheck(unittest.TestCase):

    def setUp(self):

        self.diff = False
        self.chk = False
        self.hostname = "1.1.1.1"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = "jbb.db"
        self.db['first_snap_id'] = None
        self.db['first_snap_id'] = None
        self.snap_del = False
        self.action = None


    @patch('logging.Logger.error')
    def test_operator_define_operator_error_1(self,mock_error):
        op = Operator()
        op.no_failed = 0
        op.define_operator(self.hostname,'all-same','mock_xpath',['ele1'],'mock_err','mock_info','mock command',True,['mock_id'], 'test_name')
        self.assertEqual(op.no_failed,1)
        mock_error.assert_called()                  #error called because the all_same requires 2 more args

    @patch('logging.Logger.error')
    def test_operator_define_operator_error_2(self, mock_error):
        op = Operator()
        op.no_failed = 0
        op.define_operator(self.hostname, 12, 'mock_xpath', ['ele1'], 'mock_err', 'mock_info', 'mock command',
                           True, ['mock_id'], 'test_name')
        self.assertEqual(op.no_failed, 1)           #attribute error
        mock_error.assert_called()

    @patch('jnpr.jsnapy.operator.Operator.all_same')
    @patch('logging.Logger.error')
    def test_operator_define_operator_error_3(self, mock_error, mock_all_same):
        mock_all_same.side_effect = etree.XPathEvalError('Xpath Mock Error')
        op = Operator()
        op.no_failed = 0
        op.define_operator(self.hostname, 'all-same', 'mock_xpath', ['ele1'], 'mock_err', 'mock_info', 'mock command',
                           True, ['mock_id'], 'test_name')
        self.assertEqual(op.no_failed, 1)       #xpathError
        mock_error.assert_called_with('\x1b[31mError in evaluating XPATH, \nComplete Message: Xpath Mock Error', extra='1.1.1.1')

    @patch('logging.Logger.error')
    def test_operator_exists_1(self, mock_error):
        with self.assertRaises(IndexError):
            op = Operator()
            op.exists('mock_path', [], 'mock_err','mock_info','mock_command',True,['mock_id'],'test_name','mock_xml1','mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_not_exists_1(self, mock_error):
        with self.assertRaises(IndexError):
            op = Operator()
            op.not_exists('mock_path', [], 'mock_err','mock_info','mock_command',True,['mock_id'], 'test_name','mock_xml1','mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_all_same_1(self, mock_error):
        with self.assertRaises(IndexError):
            op = Operator()
            op.all_same('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'],'test_name', 'mock_xml1',
                          'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_is_equal_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.is_equal('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                        'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_not_equal_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.not_equal('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                        'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_in_range_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.in_range('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                        'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_not_range_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.not_range('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                        'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_is_in_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.is_in('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                        'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_not_in_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.not_in('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                     'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_is_gt_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.is_gt('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                      'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_is_lt_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.is_lt('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                      'mock_xml2')
            mock_error.assert_called()

    @patch('logging.Logger.error')
    def test_operator_contains_1(self, mock_error):
        with self.assertRaises(Exception):
            op = Operator()
            op.contains('mock_path', [], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                      'mock_xml2')
            mock_error.assert_called()

    @patch('jnpr.jsnapy.operator.Operator._print_result')
    @patch('jnpr.jsnapy.operator.Operator._find_xpath')
    @patch('logging.Logger.error')
    def test_operator_no_diff_1(self, mock_error, mock_xpath, mock_result):
        mock_xpath.return_value = ['mock_pre'], ['mock_post']
        op = Operator()
        op.no_diff('mock_path', ['no node'], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                  'mock_xml2')
        mock_error.assert_called()
        mock_result.assert_called()

    @patch('jnpr.jsnapy.operator.Operator._print_result')
    @patch('jnpr.jsnapy.operator.Operator._find_xpath')
    @patch('logging.Logger.error')
    def test_operator_no_diff_2(self, mock_error, mock_xpath, mock_print):
        mock_xpath.return_value = None , ['mock_post']
        op = Operator()
        op.no_diff('mock_path', ['mock_node'], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1',
                   'mock_xml2')
        mock_error.assert_called()
        mock_print.assert_called()

    @patch('jnpr.jsnapy.operator.Operator._print_message')
    @patch('jnpr.jsnapy.operator.Operator._get_nodevalue')
    @patch('jnpr.jsnapy.operator.Operator._print_result')
    @patch('jnpr.jsnapy.operator.Operator._get_data')
    @patch('jnpr.jsnapy.operator.Operator._find_xpath')
    def test_operator_list_not_less_1(self, mock_xpath, mock_data, mock_print, mock_getnode, mock_printMessage):
        mock_xpath.return_value = ['mock_pre'], ['mock_post']

        mock_data.return_value = {(('mock_node_value',),):'mock_Element'}
        mock_getnode.return_value = {}, {}
        op = Operator()
        op.list_not_less('mock_path', ['no node'], 'mock_err', 'mock_info', 'mock_command', True, ['mock_id'], 'test_name', 'mock_xml1', 'mock_xml2')
        mock_printMessage.assert_called()
        mock_print.assert_called()

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_no_more_not_node(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list_not_more_no_node.yml')
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
            "pre_list_not_more_no_node",
            self.action,
            "post_list_not_more_no_node")
        self.assertEqual(oper.no_passed, 1)
        self.assertEqual(oper.no_failed, 0)

    @patch('jnpr.jsnapy.check.get_path')
    def test_list_not_more_missing_node(self, mock_path):
        self.chk = True
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_list_not_more_node_missing.yml')
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
            "pre_list_not_more_node_missing",
            self.action,
            "post_list_not_more_node_missing")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 1)

    @patch('logging.Logger.error')
    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_Index_error(self, mock_path, mock_error):
        with self.assertRaises(Exception):
            self.chk = True
            comp = Comparator()                 #created changes in the test file
            conf_file = os.path.join(os.path.dirname(__file__),
                                     'configs', 'main_test_delta_index_error.yml')
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
                "pre_list_not_more_no_node",
                self.action,
                "post_list_not_more_no_node")

    @patch('logging.Logger.error')
    @patch('jnpr.jsnapy.check.get_path')
    def test_delta_percentage(self, mock_path, mock_error):
        self.chk = True
        comp = Comparator()  # created changes in the test file
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_delta_percentage.yml')
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
            "pre_delta_percentage",
            self.action,
            "post_delta_percentage")
        self.assertEqual(oper.no_passed, 0)
        self.assertEqual(oper.no_failed, 6)   

    @patch('jnpr.jsnapy.check.get_path')
    def test_regex_errors(self, mock_path):
        with self.assertRaises(IndexError):
            self.chk = True
            comp = Comparator()  # created changes in the test file
            conf_file = os.path.join(os.path.dirname(__file__),
                                     'configs', 'main_regex.yml')
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
                "pre_regex",
                self.action,
                "post_regex_empty")

    @patch('jnpr.jsnapy.check.get_path')
    def test_regex_errors_1_(self, mock_path):

        self.chk = True
        comp = Comparator()  # created changes in the test file
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_regex_1.yml')
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
            "pre_regex",
            self.action,
            "post_regex_empty")
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_regex_pass(self, mock_path):
        self.chk = True
        comp = Comparator()  # created changes in the test file
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_regex_2.yml')
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
            "pre_regex_pass",
            self.action,
            "post_regex_pass")
        self.assertEqual(oper.no_passed, 1)
   
    @patch('jnpr.jsnapy.check.get_path')
    def test_regex_ignore_null_true(self, mock_path):
        self.chk = True
        comp = Comparator()  # created changes in the test file
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_regex_1.yml')
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
            "pre_regex",
            self.action,
            "post_regex_empty")
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_regex_no_postnode_in_xpath(self, mock_path):
        self.chk = True
        comp = Comparator()  # created changes in the test file
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_regex_1.yml')
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
            "pre_regex_pass",
            self.action,
            "post_regex_xpath_no_node")
        self.assertEqual(oper.no_failed, 1)

    @patch('jnpr.jsnapy.check.get_path')
    def test_xml_comparator(self, mock_path):
        self.chk = True
        comp = Comparator()  # created changes in the test file
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_xml_comparator.yml')
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
            "pre_xml_compare",
            self.action,
            "post_xml_compare")
        self.assertEqual(oper.no_failed,1)
