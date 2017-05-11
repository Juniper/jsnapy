import unittest
import os
import yaml
from jnpr.jsnapy.check import Comparator
from mock import patch, MagicMock
from nose.plugins.attrib import attr

@attr('unit')
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
    @patch('jnpr.jsnapy.check.get_path')
    def test_incorrect_test_file(self, mock_path, mock_info):
        self.chk = False
        #mimicking the testfiles path found in the jsanpy.cfg
        mock_path.return_value = os.path.join('/etc', 'jsnapy', 'testfiles')
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
            self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('sys.exit')
    @patch('logging.Logger.info')
    @patch('jnpr.jsnapy.sqlite_get.get_path')
    def test_incorrect_test_format(self, mock_path, mock_info, mock_sys):
        def fun():
            raise BaseException
        mock_sys.return_value = fun
        self.chk = True
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
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
        with patch('jnpr.jsnapy.check.diff') as mock_compare:
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
    

    @patch('jnpr.jsnapy.check.get_path')
    def test_conditional_operator_fail(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_conditional_op_fail.yml')
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
        self.assertEqual(oper.no_passed, 3) #one not run due to short-cutting
        self.assertEqual(oper.no_failed, 0)
        self.assertEqual(oper.result, "Failed")
    

    @patch('jnpr.jsnapy.check.get_path')
    def test_conditional_operator_error_1(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_conditional_op_error_1.yml')
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
        self.assertEqual(oper.no_passed, 4) #one not run due to short-cutting
        self.assertEqual(oper.no_failed, 0)
        self.assertEqual(oper.result, "Failed")

    @patch('jnpr.jsnapy.check.get_path')
    def test_conditional_operator_error_2(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_conditional_op_error_2.yml')
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
        self.assertEqual(oper.result, None)
    

    @patch('jnpr.jsnapy.check.get_path')
    def test_conditional_operator_error_3(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_conditional_op_error_3.yml')
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
        self.assertEqual(oper.no_passed, 3) 
        self.assertEqual(oper.no_failed, 0)
        self.assertEqual(oper.result, 'Passed')
    

    @patch('jnpr.jsnapy.check.get_path')
    def test_conditional_operator_error_4(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_conditional_op_error_4.yml')
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
        self.assertEqual(oper.no_passed, 3) 
        self.assertEqual(oper.no_failed, 0)
        self.assertEqual(oper.result, 'Passed')
    
    @patch('jnpr.jsnapy.check.get_path')
    def test_conditional_operator_pass(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_conditional_op_pass.yml')
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
        self.assertEqual(oper.no_passed, 4) 
        self.assertEqual(oper.no_failed, 0)
        self.assertEqual(oper.result, 'Passed')

    @patch('jnpr.jsnapy.check.get_path')
    def test_dynamic_info_err_msg_1(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_is-gt_ignore-null_fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        path = {'info': "Test Succeeded!! cpu total is greater than $1 and its value is {{post['cpu-total']}}", 'is-gt': 'cpu-total, 1', 'err': "Test Failed!!! cpu total is less than $1 and its value is {{post['cpu-total']}}"}
        ele_list = ['cpu-total', '1']
        info = comp.get_info_mssg(path,ele_list)
        err = comp.get_err_mssg(path,ele_list)
        self.assertEqual(info,"Test Succeeded!! cpu total is greater than 1 and its value is {{post['cpu-total']}}")
        self.assertEqual(err,"Test Failed!!! cpu total is less than 1 and its value is {{post['cpu-total']}}")

    @patch('jnpr.jsnapy.check.get_path')
    def test_dynamic_info_err_msg_2(self, mock_path):
        self.chk = False
        comp = Comparator()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_not-range_ignore-null_fail.yml')
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        config_file = open(conf_file, 'r')
        main_file = yaml.load(config_file)
        path = {'info': "Test Succeeded!! memory heap utilisation of the FPCs is within the range of $1-$2% and its value is {{post['memory-heap-utilization']}}", 'not-range': 'memory-heap-utilization, 0, 30', 'err': "Test Failed!!! memory heap utilisation of the FPCs is not within the range of $1-$2% and its value is {{post['memory-heap-utilization']}}"}
        ele_list = ['cpu-total', '1']
        info = comp.get_info_mssg(path,ele_list)
        err = comp.get_err_mssg(path,ele_list)
        self.assertEqual(info,"Test Succeeded!! memory heap utilisation of the FPCs is within the range of 0-30% and its value is {{post['memory-heap-utilization']}}")
        self.assertEqual(err,"Test Failed!!! memory heap utilisation of the FPCs is not within the range of 0-30% and its value is {{post['memory-heap-utilization']}}")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCheck)
    unittest.TextTestRunner(verbosity=2).run(suite)
