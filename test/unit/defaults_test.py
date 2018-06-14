from unittest.mock import (
    patch, call
)
from pytest import raises

from azure_li_services.defaults import Defaults
from azure_li_services.exceptions import AzureHostedConfigFileNotFoundException


class TestDefaults(object):
    @patch('os.path.exists')
    def test_get_config_file(self, mock_os_path_exists):
        mock_os_path_exists.return_value = True
        assert Defaults.get_config_file() == '/etc/suse_firstboot_config.yaml'
        mock_os_path_exists.return_value = False
        with raises(AzureHostedConfigFileNotFoundException):
            Defaults.get_config_file()

    def test_get_status_report_directory(self):
        assert Defaults.get_status_report_directory() == \
            '/var/lib/azure_li_services'

    @patch('azure_li_services.defaults.Command.run')
    def test_mount_config_source_fallback(self, mock_Command_run):
        command_result = [True, False]

        def side_effect(self):
            if not command_result.pop():
                raise Exception

        mock_Command_run.side_effect = side_effect
        Defaults.mount_config_source()
        assert mock_Command_run.call_args_list == [
            call(['mount', '--label', 'azconfig', '/mnt']),
            call(['mount', '/dev/dvd', '/mnt'])
        ]
