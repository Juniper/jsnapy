import unittest
from jnpr.jsnapy import SnapAdmin
from mock import patch


class TestModule(unittest.TestCase):

    def setUp(self):
        self.js = SnapAdmin()

    @patch('jnpr.jsnapy.SnapAdmin.extract_data')
    def test_snap(self, mock_extract_data):
        config_file = "/configs/config_module_snap.yml"
        snap_file = "pre"
        self.js.snap(config_file, snap_file)
        self.assertTrue(mock_extract_data.called)

    @patch('jnpr.jsnapy.SnapAdmin.extract_dev_data')
    def test_snap_dev(self, mock_extract_dev):
        config_file = "/configs/config_module_snap.yml"
        snap_file = "pre"
        self.js.snap()

with patch('logging.Logger.info') as mock_logger:
    if __name__ == "__main__":
        suite = unittest.TestLoader().loadTestsFromTestCase(TestModule)
        unittest.TextTestRunner(verbosity=2).run(suite)
