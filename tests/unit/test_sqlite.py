import unittest
import os
from jnpr.jsnap.sqlite_store import JsnapSqlite
from jnpr.jsnap.sqlite_get import SqliteExtractXml
from mock import patch


class TestSqlite(unittest.TestCase):

    def setUp(self):
        self.diff = False
        self.hostname = "10.216.193.114"
        self.db = "mock_test.db"
        self.db_dict2 = dict()
        self.db_dict2['username'] = "mock_test"
        self.db_dict2['cli_command'] = "show version"
        self.db_dict2['snap_name'] = "mock_snap"
        self.db_dict2['filename'] = "file_mock"
        self.db_dict2['format'] = "text"
        self.db_dict2['data'] = "mock_data"

    def tearDown(self):
        path = os.getcwd()
        db_filename = os.path.join(path, 'snapshots', "mock_test.db")
        os.remove(db_filename)

    @patch('sys.exit')
    def test_sqlite_1(self, mock_sys):

        js = JsnapSqlite("10.216.193.114", self.db)
        js.insert_data(self.db_dict2)
        with patch('logging.Logger.error') as mock_log:
            extr = SqliteExtractXml(self.db)
            data, formt = extr.get_xml_using_snapname(
                "10.216.193.114", self.db_dict2['cli_command'], self.db_dict2['snap_name'])
            self.assertEqual(data, "mock_data")
            self.assertEqual(formt, "text")
            extr.get_xml_using_snapname(
                "10.216.193.114",
                self.db_dict2['cli_command'],
                "mock_ssssnap")
            err = [
                "No previous snapshots exists with name = mock_ssssnap for command = show version"]
            c_list = mock_log.call_args_list[0]
            self.assertNotEqual(c_list[0][0].find(err[0]), -1)

    @patch('sys.exit')
    def test_sqlite_2(self, mock_sys):

        def fun():
            raise BaseException
        mock_sys.return_value = fun
        js = JsnapSqlite("10.216.193.114", self.db)
        js.insert_data(self.db_dict2)
        with patch('logging.Logger.error') as mock_log:
            try:
                extr = SqliteExtractXml(self.db)
                extr.get_xml_using_snapname(
                    "10.216.193.11",
                    self.db_dict2['cli_command'],
                    self.db_dict2['snap_name'])
            except BaseException:
                err = "No previous snapshots exists for host 10.216.193.11"
                c_list = mock_log.call_args_list[0]
                self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('sys.exit')
    def test_sqlite_3(self, mock_sys):
        js = JsnapSqlite("10.216.193.114", self.db)
        js.insert_data(self.db_dict2)
        with patch('logging.Logger.error') as mock_log:
            extr = SqliteExtractXml(self.db)
            data, formt = extr.get_xml_using_snap_id(
                "10.216.193.114", self.db_dict2['cli_command'], 0)
            self.assertEqual(data, "mock_data")
            self.assertEqual(formt, "text")
            extr.get_xml_using_snap_id("10.216.193.114", "show vers", 0)
            err = [
                "No previous snapshots exists with id = 0 for command = show vers"]
            c_list = mock_log.call_args_list[0]
            self.assertNotEqual(c_list[0][0].find(err[0]), -1)

    @patch('sys.exit')
    def test_sqlite_4(self, mock_sys):
        def fun():
            raise BaseException
        mock_sys.return_value = fun
        js = JsnapSqlite("10.216.193.114", self.db)
        js.insert_data(self.db_dict2)
        with patch('logging.Logger.error') as mock_log:
            try:
                extr = SqliteExtractXml(self.db)
                extr.get_xml_using_snap_id(
                    "10.216.193.11",
                    self.db_dict2['cli_command'],
                    0)
            except BaseException:
                err = "No previous snapshots exists for host 10.216.193.11"
                c_list = mock_log.call_args_list[0]
                self.assertNotEqual(c_list[0][0].find(err), -1)


suite = unittest.TestSuite()
suite.addTest(TestSqlite("test_sqlite_1"))
suite.addTest(TestSqlite("test_sqlite_2"))
suite.addTest(TestSqlite("test_sqlite_3"))
suite.addTest(TestSqlite("test_sqlite_4"))
unittest.TextTestRunner().run(suite)
