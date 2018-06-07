from unittest.mock import (
    patch, call, Mock
)
from pytest import raises
from azure_li_services.units.config_lookup import main
from azure_li_services.exceptions import AzureHostedConfigFileNotFoundException


class TestConfigLookup(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.path.Path.create')
    @patch('azure_li_services.path.Path.which')
    @patch('azure_li_services.units.config_lookup.StatusReport')
    @patch('os.chmod')
    def test_main(
        self, mock_chmod, mock_StatusReport, mock_Path_which,
        mock_Path_create, mock_Command_run
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        main()
        mock_StatusReport.assert_called_once_with('config_lookup')
        status.set_success.assert_called_once_with()
        assert mock_Command_run.call_args_list == [
            call(['mount', '--label', 'azconfig', '/mnt']),
            call([
                'cp', mock_Path_which.return_value,
                '/etc/suse_firstboot_config.yaml'
            ]),
            call(['umount', '/mnt'])
        ]
        mock_chmod.assert_called_once_with(
            '/etc/suse_firstboot_config.yaml', 0o600
        )
        mock_Path_create.assert_called_once_with('/etc')
        mock_Path_which.assert_called_once_with(
            'suse_firstboot_config.yaml', ['/mnt']
        )

    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.path.Path.which')
    @patch('azure_li_services.units.config_lookup.StatusReport')
    def test_main_raises(self, mock_StatusReport, mock_Path_which, mock_Command_run):
        mock_Path_which.return_value = None
        with raises(AzureHostedConfigFileNotFoundException):
            main()
