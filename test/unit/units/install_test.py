from unittest.mock import (
    patch, call, Mock
)
from azure_li_services.units.install import main


class TestInstall(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.install.Defaults.get_config_file')
    @patch('azure_li_services.units.install.Path.create')
    @patch('azure_li_services.units.install.glob.iglob')
    def test_main(
        self, mock_iglob, mock_Path_create, mock_get_config_file,
        mock_Command_run
    ):
        command_result = Mock()
        command_result.output = 'foo'
        mock_Command_run.return_value = command_result
        mock_iglob.return_value = ['/var/lib/localrepos/azure_packages/foo.rpm']
        mock_get_config_file.return_value = '../data/config.yaml'
        main()
        mock_Path_create.assert_called_once_with(
            '/var/lib/localrepos/azure_packages'
        )
        assert mock_Command_run.call_args_list == [
            call(['mount', '--label', 'azconfig', '/mnt']),
            call(
                [
                    'rsync', '-zav', '/directory-with-rpm-files/*',
                    '/another-directory-with-rpm-files/*',
                    '/var/lib/localrepos/azure_packages'
                ]
            ),
            call(['createrepo', '/var/lib/localrepos/azure_packages']),
            call(
                ['zypper', 'removerepo', 'azure_packages'],
                raise_on_error=False
            ),
            call(
                [
                    'zypper', 'addrepo', '--no-gpgcheck',
                    '/var/lib/localrepos/azure_packages', 'azure_packages'
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
                    'zypper', '--non-interactive', 'install',
                    '--auto-agree-with-licenses', 'foo'
                ]
            ),
            call(['umount', '/mnt'])
        ]
