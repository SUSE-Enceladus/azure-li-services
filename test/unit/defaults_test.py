from unittest.mock import (
    patch, call, Mock
)
from pytest import raises

from azure_li_services.defaults import Defaults
from azure_li_services.exceptions import (
    AzureHostedConfigFileNotFoundException,
    AzureHostedConfigFileSourceMountException
)


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
    def test_mount_config_source(self, mock_Command_run):
        mount_result = Mock()
        mount_result.returncode = 0
        mock_Command_run.return_value = mount_result

        result = Defaults.mount_config_source()
        assert result.name == 'suse_firstboot_config.yaml'
        assert result.location == '/mnt'
        assert result.label == 'azconfig'

        mount_result.returncode = 1

        with raises(AzureHostedConfigFileSourceMountException):
            Defaults.mount_config_source()
            assert mock_Command_run.call_args_list == [
                call(
                    ['mount', '--label', 'azconfig', '/mnt'],
                    raise_on_error=False
                ),
                call(['mount', '/dev/dvd', '/mnt'])
            ]

    @patch('azure_li_services.status_report.StatusReport')
    def test_get_service_reports(self, mock_StatusReport):
        Defaults.get_service_reports()
        assert mock_StatusReport.call_args_list == [
            call(
                'call',
                systemd_service_name='azure-li-call',
                init_state=False
            ),
            call(
                'config_lookup',
                systemd_service_name='azure-li-config-lookup',
                init_state=False
            ),
            call(
                'install',
                systemd_service_name='azure-li-install',
                init_state=False
            ),
            call(
                'machine_constraints',
                systemd_service_name='azure-li-machine-constraints',
                init_state=False
            ),
            call(
                'network',
                systemd_service_name='azure-li-network',
                init_state=False
            ),
            call(
                'storage',
                systemd_service_name='azure-li-storage',
                init_state=False
            ),
            call(
                'system_setup',
                systemd_service_name='azure-li-system-setup',
                init_state=False
            ),
            call(
                'user',
                systemd_service_name='azure-li-user',
                init_state=False
            )
        ]
