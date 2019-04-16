import unittest
import os
import sys
import yaml
from mock import patch, MagicMock
from nose.plugins.attrib import attr
from jnpr.jsnapy import get_config_location, get_path, DirStore
@attr('unit')
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
    @patch('os.path.isfile')
    def test_config_location_env(self, mock_is_file):
        os.environ['JSNAPY_HOME'] = os.path.join('bogus', 'path')
        mock_is_file.side_effect = lambda arg: arg == os.path.join('bogus', 'path', 'jsnapy.cfg')
        loc = get_config_location()
        self.assertEqual(loc, os.path.join('bogus', 'path'))

    @patch('os.path.isfile')
    def test_config_location_home(self, mock_is_file):
        mock_is_file.side_effect = lambda arg: arg == os.path.join(os.path.expanduser('~'),'.jsnapy','jsnapy.cfg')
        loc = get_config_location()
        self.assertEqual(loc,os.path.join(os.path.expanduser('~'),'.jsnapy'))

    @patch('os.path.isfile')
    def test_config_location_etc(self, mock_is_file):
        if hasattr(sys, 'real_prefix'):
            mock_is_file.side_effect = lambda arg: arg in [os.path.join(sys.prefix, 'etc',
                                                                        'jsnapy',
                                                      'jsnapy.cfg')]
            loc = get_config_location()
            self.assertEqual(loc, os.path.join(sys.prefix, 'etc', 'jsnapy'))
        elif 'win32' in sys.platform:
            mock_is_file.side_effect = lambda arg: arg in [os.path.join(os.path.expanduser('~'),
                                                                        'jsnapy', 'jsnapy.cfg')]
            loc = get_config_location()
            self.assertEqual(loc, os.path.join(os.path.expanduser('~'),'jsnapy'))
        else:
            mock_is_file.side_effect = lambda arg: arg in ['/etc/jsnapy/jsnapy.cfg']
            loc = get_config_location()
            self.assertEqual(loc, '/etc/jsnapy')

    @patch('os.path.isfile')   #new
    def test_config_location_wrong_path(self, mock_is_file):
        with self.assertRaises(Exception):
            mock_is_file.side_effect = lambda arg: arg == '/xyz'
            loc = get_config_location()

    @patch('jnpr.jsnapy.get_config_location')  #new
    def test_get_path_config_exception(self, mock_config_location):
        with self.assertRaises(Exception):
            DirStore.custom_dir = None
            mock_config_location.return_value = None
            loc = get_path('DEFAULT','config_file_path')

    @patch('jnpr.jsnapy.get_config_location')
    def test_get_path_normal(self, mock_config_location):
        DirStore.custom_dir = None
        mock_config_location.return_value = os.path.join(os.path.dirname(__file__),'configs')
        loc = get_path('DEFAULT','config_file_path')
        self.assertTrue(mock_config_location.called)
        self.assertEqual(loc,'/throgus')

    @patch('jnpr.jsnapy.get_config_location')
    def test_get_path_custom(self, mock_config_loc):
        DirStore.custom_dir = '~/bogus'
        if 'win32' in sys.platform:
            HOME = os.path.join(os.path.expanduser('~'), 'bogus\\')
        else:
            HOME = os.path.join(os.path.expanduser('~'), 'bogus/')
        conf_loc = get_path('DEFAULT', 'config_file_path')
        snap_loc = get_path('DEFAULT', 'snapshot_path')
        test_loc = get_path('DEFAULT', 'test_file_path')

        self.assertEqual(conf_loc, HOME)
        self.assertEqual(snap_loc, os.path.join(HOME, 'snapshots'))
        self.assertEqual(test_loc, os.path.join(HOME, 'testfiles'))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCheck)
    unittest.TextTestRunner(verbosity=2).run(suite)
