import unittest
import yaml
import os
from jnpr.jsnapy.snap import Parser
from jnpr.junos.device import Device
from jnpr.jsnapy import SnapAdmin
import jnpr.junos.device
from mock import patch, mock_open, ANY, call, MagicMock
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

    @patch('logging.Logger.info')
    def test_write_file(self, mock_info):
        par = Parser()
        res = par._check_reply(True, 'xml')
        self.assertEqual(res,'')
        mock_info.assert_called()

    @patch('logging.Logger.error')
    @patch('ncclient.manager.connect')
    def test_generate_reply_error_1(self, mock_dev, mock_err):
        par = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'bogus_testfile_1.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = Device(user='10.216.193.114', host='abc', passwd='xyz')
        dev.open()
        par.generate_reply(test_file, dev, '10.216.193.114_snap_mock' ,self.hostname, self.db )
        mock_err.assert_called()

    @patch('logging.Logger.error')
    @patch('ncclient.manager.connect')
    def test_generate_reply_error_2(self, mock_dev, mock_err):
        par = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'bogus_testfile_2.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = Device(user='10.216.193.114', host='abc', passwd='xyz')
        dev.open()
        par.generate_reply(test_file, dev, '10.216.193.114_snap_mock', self.hostname, self.db)
        mock_err.assert_called()

    @patch('jnpr.jsnapy.snap.Parser._write_warning')
    @patch('jnpr.junos.rpcmeta._RpcMetaExec.cli')
    @patch('logging.Logger.error')
    @patch('lxml.etree.tostring')
    @patch('ncclient.manager.connect')
    def test_generate_reply_error_3(self, mock_dev,mock_tostring, mock_err, mock_cli, mock_write_warn):
        from jnpr.junos.exception import RpcError
        mock_cli.side_effect = RpcError
        par = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'bogus_testfile_3.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = Device(host='10.221.136.250', user='abc', passwd='xyz')
        dev.open()
        par.generate_reply(test_file, dev, 'mock.xml', self.hostname, self.db)
        mock_err.assert_called()
        mock_write_warn.assert_called()

    @patch('jnpr.jsnapy.snap.Parser._write_warning')
    @patch('jnpr.junos.rpcmeta._RpcMetaExec.__getattr__')
    @patch('logging.Logger.error')
    @patch('lxml.etree.tostring')
    @patch('ncclient.manager.connect')
    def test_generate_reply_rpc_error_4(self, mock_dev, mock_tostring, mock_err, mock_rpc, mock_write_warn):
        from jnpr.junos.exception import RpcError
        mock_rpc.side_effect = RpcError
        par = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'bogus_testfile_4.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = Device(host='10.221.136.250', user='abc', passwd='xyz')
        dev.open()
        par.generate_reply(test_file, dev, 'mock.xml', self.hostname, self.db)
        mock_err.assert_called()
        mock_write_warn.assert_called()

    @patch('jnpr.jsnapy.snap.Parser._write_warning')
    @patch('jnpr.junos.rpcmeta._RpcMetaExec.__getattr__')
    @patch('logging.Logger.error')
    @patch('lxml.etree.tostring')
    @patch('ncclient.manager.connect')
    def test_generate_reply_rpc_error_5(self, mock_dev, mock_tostring, mock_err, mock_rpc, mock_write_warn):
        from jnpr.junos.exception import RpcError
        mock_rpc.side_effect = RpcError
        par = Parser()
        test_file = os.path.join(os.path.dirname(__file__),
                                 'configs', 'bogus_testfile_5.yml')
        test_file = open(test_file, 'r')
        test_file = yaml.load(test_file)
        dev = Device(host='10.221.136.250', user='abc', passwd='xyz')
        dev.open()
        par.generate_reply(test_file, dev, 'mock.xml', self.hostname, self.db)
        mock_err.assert_called()
        mock_write_warn.assert_called()

    @patch('logging.Logger.info')
    def test_write_file_rpc_reply_true(self, mock_log):
        par = Parser()
        par._write_file(True,'xml','mock.xml')
        c = mock_log.call_args_list[0]
        self.assertNotEqual(
            c[0][0].find("Output of requested Command/RPC is empty"), -1)

    @patch('jnpr.jsnapy.snap.Parser.store_in_sqlite')
    def test_write_warning(self, mock_store_data):
        self.db['store_in_sqlite'] = True
        par = Parser()
        par._write_warning("mock_reply", self.db, 'mock.xml',self.hostname
                           ,'mock_cmd','text','mock_output')
        mock_store_data.assert_called()

