from pytest import raises
from unittest.mock import (
    Mock, patch, call
)
from azure_li_services.units.user import main
from azure_li_services.runtime_config import RuntimeConfig

from azure_li_services.exceptions import (
    AzureHostedException,
    AzureHostedUserConfigDataException
)


class TestUser(object):
    def setup(self):
        self.config = RuntimeConfig('../data/config.yaml')

    @patch('azure_li_services.units.user.Command.run')
    @patch('azure_li_services.defaults.Defaults.mount_config_source')
    @patch('azure_li_services.units.user.Defaults.get_config_file')
    @patch('azure_li_services.units.user.RuntimeConfig')
    @patch('azure_li_services.units.user.Users')
    @patch('azure_li_services.units.user.Path.create')
    @patch('azure_li_services.units.user.StatusReport')
    @patch('os.path.exists')
    @patch('os.chmod')
    @patch('os.chown')
    @patch('pwd.getpwnam')
    @patch('grp.getgrnam')
    def test_main(
        self, mock_getgrnam, mock_getpwnam, mock_chown, mock_chmod,
        mock_path_exists, mock_StatusReport, mock_Path_create,
        mock_Users, mock_RuntimConfig, mock_get_config_file,
        mock_mount_config_source,
        mock_Command_run
    ):
        group_exists = [True, False, False]
        user_exists = [True, True, True, False]

        def side_effect_group_exists(group):
            return group_exists.pop()

        def side_effect_user_exists(user):
            return user_exists.pop()

        status = Mock()
        mock_StatusReport.return_value = status
        mock_path_exists.return_value = True
        mock_RuntimConfig.return_value = self.config
        mock_mount_config_source.return_value.location = 'config_mount'
        with patch('builtins.open', create=True) as mock_open:
            system_users = Mock()
            system_users.group_exists.side_effect = side_effect_group_exists
            system_users.user_exists.side_effect = side_effect_user_exists
            mock_Users.return_value = system_users
            main()
            mock_mount_config_source.assert_called_once_with()
            mock_StatusReport.assert_called_once_with('user')
            status.set_success.assert_called_once_with()
            file_handle = mock_open.return_value.__enter__.return_value
            assert system_users.group_exists.call_args_list == [
                call('admin'), call('nogroup'), call('admin')
            ]
            system_users.user_add.assert_called_once_with(
                'hanauser', [
                    '-p', 'sha-512-cipher',
                    '-s', '/bin/bash',
                    '-m', '-d', '/home/hanauser'
                ]
            )
            assert system_users.user_modify.call_args_list == [
                call('hanauser', ['-a', '-G', 'admin']),
                call(
                    'rpc', [
                        '-g', 'nogroup',
                        '-s', '/sbin/nologin',
                        '-u', '495'
                    ]
                ),
                call(
                    'root', ['-p', 'sha-512-cipher', '-s', '/bin/bash']
                ),
                call(
                    'nopasslogin', ['-s', '/bin/bash']
                )
            ]
            system_users.setup_change_password_on_logon.assert_called_once_with(
                'hanauser'
            )
            assert system_users.group_add.call_args_list == [
                call('admin', []),
                call('nogroup', ['-g', '4711'])
            ]
            assert mock_open.call_args_list == [
                call('/home/hanauser/.ssh/authorized_keys', 'a'),
                call('/root/.ssh/authorized_keys', 'a'),
                call('/home/nopasslogin/.ssh/authorized_keys', 'a'),
                call('/etc/sudoers', 'a')
            ]
            assert file_handle.write.call_args_list == [
                call('\n'),
                call('ssh-rsa foo'),
                call('\n'),
                call('ssh-rsa foo'),
                call('\n'),
                call('ssh-rsa foo'),
                call('\n'),
                call('%admin ALL=(ALL) NOPASSWD: ALL')
            ]
            assert mock_Command_run.call_args_list == [
                call(
                    [
                        'cp', 'config_mount/path/to/private/key/id_dsa',
                        '/home/hanauser/.ssh/'
                    ]
                )
            ]
            assert mock_chmod.call_args_list == [
                call('/home/hanauser/.ssh/', 0o700),
                call('/home/hanauser/.ssh/authorized_keys', 0o600),
                call('/home/hanauser/.ssh/id_dsa', 0o600),
                call('/root/.ssh/', 0o700),
                call('/root/.ssh/authorized_keys', 0o600),
                call('/home/nopasslogin/.ssh/', 0o700),
                call('/home/nopasslogin/.ssh/authorized_keys', 0o600)
            ]
            assert mock_chown.call_args_list == [
                call(
                    '/home/hanauser/.ssh/',
                    mock_getpwnam.return_value.pw_uid,
                    mock_getgrnam.return_value.gr_gid
                ),
                call(
                    '/home/hanauser/.ssh/authorized_keys',
                    mock_getpwnam.return_value.pw_uid,
                    mock_getgrnam.return_value.gr_gid
                ),
                call(
                    '/home/hanauser/.ssh/id_dsa',
                    mock_getpwnam.return_value.pw_uid,
                    mock_getgrnam.return_value.gr_gid
                ),
                call(
                    '/home/nopasslogin/.ssh/',
                    mock_getpwnam.return_value.pw_uid,
                    mock_getgrnam.return_value.gr_gid
                ),
                call(
                    '/home/nopasslogin/.ssh/authorized_keys',
                    mock_getpwnam.return_value.pw_uid,
                    mock_getgrnam.return_value.gr_gid
                )
            ]

            with raises(AzureHostedException):
                group_exists = [True, False, False]
                user_exists = [True, True, False]
                system_users.user_modify.side_effect = Exception
                main()

            system_users.user_modify.reset_mock()
            with raises(AzureHostedException):
                group_exists = [True, False, False]
                user_exists = [True, True, False]
                mock_mount_config_source.side_effect = Exception
                main()

            system_users.setup_change_password_on_logon.reset_mock()
            with raises(AzureHostedException):
                group_exists = [True, False, False]
                user_exists = [True, True, False]
                system_users.setup_change_password_on_logon.side_effect = \
                    Exception
                main()

            mock_mount_config_source.reset_mock()
            with raises(AzureHostedException):
                group_exists = [True, False, False]
                user_exists = [True, True, False]
                system_users.group_add.side_effect = Exception
                main()

    @patch('azure_li_services.units.user.Defaults.get_config_file')
    @patch('azure_li_services.units.user.RuntimeConfig')
    @patch('azure_li_services.units.user.StatusReport')
    def test_main_raises_on_missing_credentials(
        self, mock_StatusReport, mock_RuntimConfig, mock_get_config_file
    ):
        config = Mock()
        config.get_user_config.return_value = None
        mock_RuntimConfig.return_value = config
        with raises(AzureHostedUserConfigDataException):
            main()

    @patch('azure_li_services.units.user.Defaults.get_config_file')
    @patch('azure_li_services.units.user.RuntimeConfig')
    @patch('azure_li_services.units.user.StatusReport')
    def test_main_raises_on_incomplete_credentials(
        self, mock_StatusReport, mock_RuntimConfig, mock_get_config_file
    ):
        config = Mock()
        config.get_user_config.return_value = [{}]
        mock_RuntimConfig.return_value = config
        with patch('builtins.open', create=True):
            with raises(AzureHostedException):
                main()
