from unittest.mock import (
    patch, call, Mock
)
from azure_li_services.units.install import main


class TestInstall(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.install.Defaults.get_config_file')
    @patch('azure_li_services.units.install.Path.create')
    @patch('azure_li_services.units.install.StatusReport')
    @patch('azure_li_services.defaults.Defaults.mount_config_source')
    @patch('azure_li_services.units.install.glob.iglob')
    @patch('os.path.isdir')
    def test_main(
        self, mock_os_path_isdir, mock_iglob, mock_mount_config_source,
        mock_StatusReport, mock_Path_create, mock_get_config_file,
        mock_Command_run
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        command_result = Mock()
        command_result.output = 'foo'
        mock_Command_run.return_value = command_result
        mock_get_config_file.return_value = '../data/config.yaml'

        mock_iglob.return_value = [
            '/var/lib/localrepos/azure_packages/foo.rpm'
        ]

        def os_path_isdir(path):
            if path == '/path/to/repo':
                return True
            else:
                return False

        mock_os_path_isdir.side_effect = os_path_isdir
        main()

        mock_StatusReport.assert_called_once_with('install')
        status.set_success.assert_called_once_with()

        assert mock_Path_create.call_args_list == [
            call('/var/lib/localrepos/azure_packages'),
            call('/var/lib/localrepos/fsf'),
            call('/var/lib/localrepos/some_repo')
        ]
        assert mock_Command_run.call_args_list == [
            call(
                [
                    'bash', '-c', 'rsync -zav {0}/directory-with-rpm-files/* '
                    '{0}/another-directory-with-rpm-files/* '
                    '/var/lib/localrepos/azure_packages'.format(
                        mock_mount_config_source.return_value.location
                    )
                ]
            ),
            call(
                [
                    'createrepo', '/var/lib/localrepos/azure_packages'
                ]
            ),
            call(
                [
                    'rpm', '-qp', '--qf', '%{NAME}',
                    '/var/lib/localrepos/azure_packages/foo.rpm'
                ]
            ),
            call(
                [
                    'rsync', '-zav', '/path/to/file.iso',
                    '/var/lib/localrepos/fsf'
                ]
            ),
            call(
                [
                    'rsync', '-zav', '/path/to/repo/',
                    '/var/lib/localrepos/some_repo'
                ]
            ),
            call(
                [
                    'zypper', 'removerepo', 'azure_packages'
                ], raise_on_error=False
            ),
            call(
                [
                    'zypper', 'addrepo', '--no-gpgcheck',
                    '/var/lib/localrepos/azure_packages', 'azure_packages'
                ]
            ),
            call(
                [
                    'zypper', 'removerepo', 'fsf'
                ], raise_on_error=False
            ),
            call(
                [
                    'zypper', 'addrepo', '--no-gpgcheck',
                    'iso:/?iso=/var/lib/localrepos/fsf', 'fsf'
                ]
            ),
            call(
                [
                    'zypper', 'removerepo', 'some_repo'
                ], raise_on_error=False
            ),
            call(
                [
                    'zypper', 'addrepo', '--no-gpgcheck',
                    '/var/lib/localrepos/some_repo', 'some_repo'
                ]
            ),
            call(
                [
                    'zypper', '--non-interactive', 'install',
                    '--auto-agree-with-licenses',
                    'foo', 'package_a', 'package_b'
                ]
            )
        ]
