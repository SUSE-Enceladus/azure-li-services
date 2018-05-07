from unittest.mock import patch
from pytest import raises

from azure_li_services.defaults import Defaults
from azure_li_services.exceptions import AzureLiConfigFileNotFoundException


class TestDefaults(object):
    @patch('os.path.exists')
    def test_get_config_file(self, mock_os_path_exists):
        mock_os_path_exists.return_value = True
        assert Defaults.get_config_file() == '/etc/suse_firstboot_config.yaml'
        mock_os_path_exists.return_value = False
        with raises(AzureLiConfigFileNotFoundException):
            Defaults.get_config_file()
