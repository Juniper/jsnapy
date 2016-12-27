import unittest
import yaml
import os
from jnpr.jsnapy.snap import Parser
from jnpr.jsnapy import SnapAdmin
import jnpr.junos.device
from mock import patch, mock_open, ANY, call, MagicMock
from contextlib import nested
from nose.plugins.attrib import attr

@attr('unit')
class TestSnap(unittest.TestCase):

    def setUp(self):
        self.diff = False
        self.hostname = "10.216.193.114"
        self.db = dict()
        self.db['store_in_sqlite'] = False
        self.db['check_from_sqlite'] = False
        self.db['db_name'] = ""
        self.db['first_snap_id'] = None
        self.db['second_snap_id'] = None
        self.output_file = "abc"
        self.logger_snap = MagicMock()

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.logging.getLogger')
    def test_snap(self, mock_log, mock_etree, mock_dev):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'delta.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            self.assertEqual(prs.command_list, ['show chassis fpc'])
            self.assertEqual(prs.rpc_list, [])
            self.assertEqual(prs.test_included, ['check_chassis_fpc'])
        dev.close()

    @patch('sys.exit')
    @patch('argparse.ArgumentParser.print_help')
    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.logging.getLogger')
    def test_snap_2(self, mock_log, mock_etree, mock_dev, mock_parser, mock_exit):
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with nested (
                patch('jnpr.jsnapy.snap.open', m_op, create=True),
                patch('jnpr.jsnapy.jsnapy.get_path')
        )as (m_open, mock_path):
            mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
            js.generate_rpc_reply(
                dev,
                self.output_file,
                "10.216.193.114",
                js.main_file)
            self.assertTrue(mock_path.called)
        dev.close()

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_snap_3(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'delta.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('jnpr.junos.rpcmeta._RpcMetaExec.cli') as mock_cli:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                command_list=[])
            mock_cli.assert_called_once_with('show chassis fpc', format='xml')

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_snap_4(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'delta_text.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('jnpr.junos.rpcmeta._RpcMetaExec.cli') as mock_cli:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                command_list=[])
            mock_cli.assert_called_once_with('show chassis fpc', format='text')

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_snap_5(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'delta_error.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('logging.Logger.error') as mock_log:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                rpc_list=[])
            c = mock_log.call_args_list[0]
            self.assertNotEqual(c[0][0].find("ERROR occurred"), -1)

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_1(self, mock_etree, mock_dev):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'test_rpc.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user_mock",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)

            self.assertEqual(prs.command_list, [])
            self.assertEqual(
                prs.rpc_list, [
                    'get-config', 'get-interface-information'])
            self.assertEqual(
                prs.test_included, [
                    'test_rpc_version', 'test_interface'])
        dev.close()

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_2(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'test_rpc.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with nested(
                patch('jnpr.junos.rpcmeta._RpcMetaExec.__getattr__'),
                patch('jnpr.junos.rpcmeta._RpcMetaExec.get_config')
        ) as (mock_rpc, mock_config):
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                rpc_list=[])
            mock_rpc.assert_called_once_with('get_interface_information')
            mock_config.assert_called_once_with(
                options={
                    'format': 'xml'},
                filter_xml=ANY)

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_3(self, mock_etree, mock_parse, mock_dev):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'test_rpc_error.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        with patch('logging.Logger.error') as mock_log:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                rpc_list=[])
            c = mock_log.call_args_list[0]
            self.assertNotEqual(
                c[0][0].find("ERROR!!, filtering rpc works only for 'get-config' rpc"), -1)
        dev.close()

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_4(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'test_rpc_2.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with nested(
                patch('jnpr.junos.rpcmeta._RpcMetaExec.__getattr__'),
                patch('jnpr.junos.rpcmeta._RpcMetaExec.get_config')
        ) as (mock_rpc, mock_config):
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                rpc_list=[])
            mock_rpc.assert_called_once_with('get_interface_information')
            mock_config.assert_called_once_with(options={'format': 'xml'})

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_5(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'test_rpc_error_2.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('logging.Logger.error') as mock_log:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            c = mock_log.call_args_list[0]

            self.assertNotEqual(c[0][0].find("ERROR occurred"), -1)

    @patch('jnpr.jsnapy.snap.Parser._write_file')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_6(self, mock_etree, mock_parse):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'test_rpc_2_error.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="xyz",
            passwd="abc")
        with patch('logging.Logger.error') as mock_log:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db)
            c = mock_log.call_args_list[0]
            self.assertNotEqual(c[0][0].find("ERROR occurred"), -1)


    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    def test_rpc_7(self, mock_etree, mock_dev):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'tests_new.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user_mock",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        command_list = []
        rpc_list = []
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                command_list,
                rpc_list)
            self.assertEqual(command_list,['show bgp neighbor'])
            self.assertEqual(rpc_list,['get-bgp-neighbor-information'])
        dev.close()
    @patch('jnpr.junos.rpcmeta._RpcMetaExec.__getattr__')
    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    def test_duplicate_command_1(self, mock_etree, mock_dev, mock_rpc):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'test_duplicate.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user_mock",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        command_list = []
        rpc_list = []
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                command_list,
                rpc_list)
            self.assertEqual(command_list,['show chassis fpc'])
            self.assertEqual(rpc_list,['get-interface-information','get-config'])
        dev.close()
    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.JsnapSqlite')
    def test_snap_sqlite_1(self, mock_sqlite, mock_etree, mock_dev):
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'delta.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = "abc.db"
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "10.216.193.114",
                self.db,
                command_list=[])
            mock_sqlite.assert_called_once_with('10.216.193.114', 'abc.db')
        dev.close()

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.__init__')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.insert_data')
    def test_snap_sqlite_2(self, mock_insert, mock_init, mock_etree, mock_dev):
        mock_init.return_value = None
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'delta.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "10.216.193.114_snap_mock",
                "01.216.193.114",
                self.db,
                rpc_list=[])
            self.assertFalse(mock_insert.called)
            self.assertFalse(mock_init.called)
        dev.close()

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.__init__')
    @patch('jnpr.jsnapy.snap.Parser._check_reply')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.insert_data')
    def test_snap_sqlite_3(
            self, mock_insert, mock_reply, mock_init, mock_etree, mock_dev):
        mock_init.return_value = None
        prs = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'delta.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = "abc.db"
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "snap_mock",
                "10.216.193.114",
                self.db,
                command_list=[])

            db_dict = dict()
            db_dict['cli_command'] = 'show_chassis_fpc'
            db_dict['snap_name'] = "snap_mock"
            db_dict['filename'] = "10.216.193.114" + \
                "_" "snap_mock" + "_" + "show_chassis_fpc" + "." + "xml"
            db_dict['format'] = "xml"
            db_dict['data'] = mock_reply()
            mock_insert.assert_called_once_with(db_dict)
        dev.close()

    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.__init__')
    @patch('jnpr.jsnapy.snap.Parser._check_reply')
    @patch('jnpr.jsnapy.snap.JsnapSqlite.insert_data')
    def test_snap_sqlite_4(
            self, mock_insert, mock_reply, mock_init, mock_etree, mock_dev):
        mock_init.return_value = None
        prs = Parser()
        calls = []
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'test_rpc.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        self.db['store_in_sqlite'] = True
        self.db['db_name'] = "abc.db"
        with patch('jnpr.jsnapy.snap.open', m_op, create=True) as m_open:
            prs.generate_reply(
                test_file,
                dev,
                "snap_mock",
                "10.216.193.114",                
                 self.db,
                 rpc_list=[])
            db_dict = dict()
            db_dict['cli_command'] = 'get-config'
            db_dict['snap_name'] = "snap_mock"
            db_dict['filename'] = "10.216.193.114" + "_" + \
                "snap_mock" + "_" + "get-config" + "." + "xml"
            db_dict['format'] = 'xml'
            db_dict['data'] = mock_reply()
            calls.append(call(db_dict))
            db_dict2 = db_dict.copy()
            db_dict2['cli_command'] = 'get-interface-information'
            db_dict2['filename'] = "10.216.193.114" + "_" + \
                "snap_mock" + "_" + "get-interface-information" + "." + "xml"
            calls.append(call(db_dict2))
            mock_insert.assert_has_calls(calls)
        dev.close()

    @patch('sys.exit')
    @patch('argparse.ArgumentParser.print_help')
    @patch('jnpr.junos.device.Device')
    @patch('jnpr.jsnapy.snap.etree')
    @patch('jnpr.jsnapy.snap.logging.getLogger')
    def test_duplicate_command_2(self, mock_log, mock_etree, mock_dev, mock_parser, mock_exit):
        js = SnapAdmin()
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'main_duplicate.yml')
        config_file = open(conf_file, 'r')
        js.main_file = yaml.load(config_file)
        dev = jnpr.junos.device.Device(
            host="10.216.193.114",
            user="user",
            passwd="xyz")
        dev.open()
        m_op = mock_open()
        with nested (
                patch('jnpr.jsnapy.snap.open', m_op, create=True),
                patch('jnpr.jsnapy.jsnapy.get_path')
        )as (m_open, mock_path):
            mock_path.return_value = os.path.join(os.path.dirname(__file__), 'configs')
            op = js.generate_rpc_reply(
                dev,
                self.output_file,
                "10.216.193.114",
                js.main_file)
            self.assertEqual(js.command_list,['show chassis fpc'])
            self.assertEqual(js.rpc_list,['get-interface-information', 'get-config'])
        dev.close()
with nested(
        patch('jnpr.jsnapy.snap.logging.getLogger'),
        patch('logging.Logger'),
        patch('jnpr.jsnapy.snap.logging.getLogger')
)as (mock_logger, mock_log, mock_log1):
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSnap)
        unittest.TextTestRunner(verbosity=2).run(suite)
