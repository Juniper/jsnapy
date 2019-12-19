import unittest
import os
import sys
from jnpr.jsnapy.sqlite_store import JsnapSqlite
from jnpr.jsnapy.sqlite_get import SqliteExtractXml
from mock import patch
from nose.plugins.attrib import attr

@attr('unit')
class TestSqlite(unittest.TestCase):
   
    @classmethod
    def setUpClass(self):
        self.diff = False
        self.hostname = "1.1.1.1"
        self.db = "mock_test.db"
        self.db_dict2 = dict()
        self.db_dict2['cli_command'] = "show version"
        self.db_dict2['snap_name'] = "mock_snap"
        self.db_dict2['filename'] = "file_mock"
        self.db_dict2['format'] = "text"
        self.db_dict2['data'] = "mock_data"
    
    @classmethod
    def tearDownClass(self):
        db_filename = os.path.join(os.path.dirname(__file__), 'configs', 'mock_test.db')
        os.remove(db_filename)

    @patch('sys.exit')
    @patch('jnpr.jsnapy.sqlite_store.get_path')
    @patch('jnpr.jsnapy.sqlite_get.get_path')
    def test_sqlite_1(self, mock_spath, mock_path, mock_sys):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_spath.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js = JsnapSqlite("1.1.1.1", self.db)
        js.insert_data(self.db_dict2)
        def fun():
            raise BaseException
        with patch('logging.Logger.error') as mock_log:
            extr = SqliteExtractXml(self.db)
            data, formt = extr.get_xml_using_snapname(
                "1.1.1.1", self.db_dict2['cli_command'], self.db_dict2['snap_name'])
            self.assertEqual(data, "mock_data")
            self.assertEqual(formt, "text")
            try:
                data, format= extr.get_xml_using_snapname(
                    "1.1.1.1",
                    self.db_dict2['cli_command'],
                    "mock_ssssnap")
            except BaseException:
                err = [
                    "No previous snapshots exists with name = mock_ssssnap for command = show version"]
                c_list = mock_log.call_args_list[0]
                self.assertNotEqual(c_list[0][0].find(err[0]), -1)


    @patch('sys.exit')
    @patch('jnpr.jsnapy.sqlite_store.get_path')
    @patch('jnpr.jsnapy.sqlite_get.get_path')
    def test_sqlite_2(self, mock_spath, mock_path, mock_sys):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_spath.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        def fun():
            raise BaseException
        mock_sys.return_value = fun
        js = JsnapSqlite("1.1.1.1", self.db)
        js.insert_data(self.db_dict2)
        with patch('logging.Logger.error') as mock_log:
            extr = SqliteExtractXml(self.db)
            extr.get_xml_using_snapname(
                "10.216.193.11",
                self.db_dict2['cli_command'],
                self.db_dict2['snap_name'])
            err = "ERROR!! Complete message is no such table: table_10__216__193__11"
            c_list = mock_log.call_args_list[0]
            self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('sys.exit')
    @patch('jnpr.jsnapy.sqlite_store.get_path')
    @patch('jnpr.jsnapy.sqlite_get.get_path')
    def test_sqlite_3(self, mock_spath, mock_path, mock_sys):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_spath.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        js = JsnapSqlite("1.1.1.1", self.db)
        js.insert_data(self.db_dict2)
        with patch('logging.Logger.error') as mock_log:
            extr = SqliteExtractXml(self.db)
            data, formt = extr.get_xml_using_snap_id(
                "1.1.1.1", self.db_dict2['cli_command'], 0)
            self.assertEqual(data, "mock_data")
            self.assertEqual(formt, "text")
            extr.get_xml_using_snap_id("1.1.1.1", "show vers", 0)
            if sys.version_info[0] <= 3 and sys.version_info[1] <= 6:
                err = ["ERROR!! Complete message is: 'NoneType' object is not iterable"]
            else :
                err = ["ERROR!! Complete message is: cannot unpack non-iterable NoneType object"]

            c_list = mock_log.call_args_list[0]
            self.assertNotEqual(c_list[0][0].find(err[0]), -1)

    @patch('sys.exit')
    @patch('jnpr.jsnapy.sqlite_store.get_path')
    @patch('jnpr.jsnapy.sqlite_get.get_path')
    def test_sqlite_4(self, mock_spath, mock_path, mock_sys):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_spath.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        def fun():
            raise BaseException
        mock_sys.return_value = fun
        js = JsnapSqlite("1.1.1.1", self.db)
        js.insert_data(self.db_dict2)
        with patch('logging.Logger.error') as mock_log:
            extr = SqliteExtractXml(self.db)
            extr.get_xml_using_snap_id(
                "10.216.193.11",
                self.db_dict2['cli_command'],
                0)
            err = "ERROR!! Complete message is: no such table: table_10__216__193__11"
            c_list = mock_log.call_args_list[0]
            self.assertNotEqual(c_list[0][0].find(err), -1)

    @patch('sys.exit')    
    @patch('logging.Logger.error')
    @patch('sqlite3.connect')
    @patch('jnpr.jsnapy.sqlite_store.get_path')
    def test_sqlite_store_db_not_exist(self, mock_path, mock_connect, mock_log, mock_sys):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_connect.side_effect = Exception("Connection not possible")
        sq = JsnapSqlite('1.1.1.1', self.db)
        c_list = mock_log.call_args_list[0]
        err = ['ERROR occurred in database']
        self.assertIn((err[0]), c_list[0][0])

    @patch('jnpr.jsnapy.sqlite_get.get_path')
    @patch('os.path.isfile')
    def test_sqlite_extractxml_db_absent(self, mock_isfile, mock_path):
        mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
        mock_isfile.return_value = False
        with patch('sys.exit') as mock_exit:
            extr = SqliteExtractXml(self.db)
            mock_exit.assert_called_with(1)
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSqlite)
    unittest.TextTestRunner(verbosity=2).run(suite)
