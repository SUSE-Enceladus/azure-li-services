from pytest import raises
from unittest.mock import (
    Mock, patch, call
)
from azure_li_services.units.user import main
from azure_li_services.exceptions import AzureHostedUserConfigDataException
from azure_li_services.runtime_config import RuntimeConfig


class TestUser(object):
    def setup(self):
        self.config = RuntimeConfig('../data/config.yaml')

    @patch('azure_li_services.units.user.Defaults.get_config_file')
    @patch('azure_li_services.units.user.RuntimeConfig')
    @patch('azure_li_services.units.user.Users')
    @patch('azure_li_services.units.user.Path.create')
    @patch('os.path.exists')
    def test_main(
        self, mock_path_exists, mock_Path_create, mock_Users,
        mock_RuntimConfig, mock_get_config_file
    ):
        mock_path_exists.return_value = True
        mock_RuntimConfig.return_value = self.config
        with patch('builtins.open', create=True) as mock_open:
            system_users = Mock()
            system_users.group_exists.return_value = False
            mock_Users.return_value = system_users
            main()
            file_handle = mock_open.return_value.__enter__.return_value
            system_users.group_exists.assert_called_once_with('nogroup')
            assert system_users.user_add.call_args_list == [
                call('hanauser', [
                    '-p', 'sha-512-cipher',
                    '-s', '/bin/bash',
                    '-m', '-d', '/home/hanauser'
                ]),
                call('rpc', [
                    '-g', 'nogroup',
                    '-s', '/sbin/nologin',
                    '-m', '-d', '/var/lib/empty',
                    '-u', '495'
                ])
            ]
            assert system_users.group_add.call_args_list == [
                call('admin', []),
                call('nogroup', [])
            ]
            system_users.user_modify.assert_called_once_with(
                'hanauser', ['-a', '-G', 'admin']
            )
            assert mock_open.call_args_list == [
                call('/home/hanauser/.ssh/authorized_keys', 'a'),
                call('/etc/sudoers', 'a')
            ]
            assert file_handle.write.call_args_list == [
                call('\n'),
                call('ssh-rsa foo'),
                call('\n'),
                call('%admin ALL=(ALL) NOPASSWD: ALL')
            ]

    @patch('azure_li_services.units.user.Defaults.get_config_file')
    @patch('azure_li_services.units.user.RuntimeConfig')
    def test_main_raises(self, mock_RuntimConfig, mock_get_config_file):
        config = Mock()
        config.get_user_config.return_value = [{}]
        mock_RuntimConfig.return_value = config
        with raises(AzureHostedUserConfigDataException):
            main()
