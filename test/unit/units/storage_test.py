import humanfriendly
from pytest import raises
from unittest.mock import (
    patch, call, Mock
)
from azure_li_services.units.storage import main
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.exceptions import AzureHostedStorageMountException


class TestStorage(object):
    def setup(self):
        self.config = RuntimeConfig('../data/config.yaml')

    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.storage.RuntimeConfig')
    @patch('azure_li_services.units.storage.Defaults.get_config_file')
    @patch('azure_li_services.units.storage.StatusReport')
    @patch('azure_li_services.units.storage.shutil.disk_usage')
    @patch('azure_li_services.units.storage.Path.create')
    def test_main(
        self, mock_Path_create, mock_disk_usage, mock_StatusReport,
        mock_get_config_file, mock_RuntimConfig, mock_Command_run
    ):
        disk_usage = Mock()
        disk_usage.free = humanfriendly.parse_size('112G', binary=True)
        mock_disk_usage.return_value = disk_usage
        status = Mock()
        mock_StatusReport.return_value = status
        mock_RuntimConfig.return_value = self.config
        with patch('builtins.open', create=True) as mock_open:
            main()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_StatusReport.assert_called_once_with('storage')
            status.set_success.assert_called_once_with()
            mock_Path_create.assert_called_once_with('/mnt/foo')
            mock_open.assert_called_once_with('/etc/fstab', 'a')
            mock_Command_run.assert_called_once_with(['mount', '-a'])
            assert file_handle.write.call_args_list == [
                call('\n'),
                call('10.250.21.12:/nfs/share /mnt/foo nfs a,b,c 0 0'),
                call('\n')
            ]
            disk_usage.free = 0
            with raises(AzureHostedStorageMountException):
                main()

    @patch('azure_li_services.units.storage.RuntimeConfig')
    @patch('azure_li_services.units.storage.Defaults.get_config_file')
    @patch('azure_li_services.units.storage.StatusReport')
    def test_main_raises(
        self, mock_StatusReport, mock_get_config_file, mock_RuntimConfig
    ):
        config = Mock()
        config.get_storage_config.return_value = [{}]
        mock_RuntimConfig.return_value = config
        with raises(AzureHostedStorageMountException):
            main()
