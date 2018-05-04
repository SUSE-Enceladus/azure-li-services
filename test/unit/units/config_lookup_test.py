from unittest.mock import (
    patch, call
)
from pytest import raises
from azure_li_services.units.config_lookup import main
from azure_li_services.exceptions import AzureLiConfigFileNotFoundException


class TestConfigLookup(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.path.Path.create')
    @patch('azure_li_services.path.Path.which')
    def test_main(self, mock_Path_which, mock_Path_create, mock_Command_run):
        main()
        assert mock_Command_run.call_args_list == [
            call(['mount', '--label', 'azconfig', '/mnt']),
            call([
                'cp', mock_Path_which.return_value, '/etc/azure_li_config.yaml'
            ]),
            call(['umount', '/mnt'])
        ]
        mock_Path_create.assert_called_once_with('/etc')
        mock_Path_which.assert_called_once_with(
            'suse_firstboot_config.yaml', ['/mnt']
        )

    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.path.Path.which')
    def test_main_raises(self, mock_Path_which, mock_Command_run):
        mock_Path_which.return_value = None
        with raises(AzureLiConfigFileNotFoundException):
            main()
