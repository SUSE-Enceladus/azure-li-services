import io
from unittest.mock import (
    patch, Mock, MagicMock, call
)
from azure_li_services.units.cleanup import main


class TestCleanup(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.cleanup.Defaults.get_service_reports')
    @patch('azure_li_services.units.cleanup.Defaults.mount_config_source')
    @patch('azure_li_services.units.cleanup.Defaults.umount_config_source')
    def test_main(
        self, mock_umount_config_source, mock_mount_config_source,
        mock_get_service_reports, mock_Command_run
    ):
        report = Mock()
        report.get_state.return_value = True
        report.get_reboot.return_value = True
        mock_get_service_reports.return_value = [report]
        with patch('builtins.open', create=True) as mock_open:
            install_source = Mock()
            install_source.location = 'lun_location'
            mock_mount_config_source.return_value = install_source
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            file_handle.read.return_value = \
                'BOOT_IMAGE=/vmlinuz-4.4.138-59-default ' + \
                'root=UUID=8ef42f26 splash=silent'
            main()
            mock_mount_config_source.assert_called_once_with()
            mock_umount_config_source.assert_called_once_with(
                install_source
            )
            assert mock_open.call_args_list == [
                call('lun_location/workload_success_is_true', 'w'),
                call('/proc/cmdline')
            ]
            assert mock_Command_run.call_args_list == [
                call(
                    [
                        'zypper', '--non-interactive',
                        'remove', '--clean-deps', '--force-resolution',
                        'azure-li-services'
                    ]
                ),
                call(
                    [
                        'systemctl', 'reset-failed'
                    ]
                ),
                call(
                    [
                        'kexec',
                        '--load', '/boot/vmlinuz',
                        '--initrd', '/boot/initrd',
                        '--command-line',
                        'root=UUID=8ef42f26 splash=silent'
                    ]
                ),
                call(
                    ['kexec', '--exec']
                )
            ]
        report.get_state.return_value = False
        mock_Command_run.reset_mock()
        with patch('builtins.open', create=True) as mock_open:
            main()
            assert mock_Command_run.call_args_list == [
                call(
                    [
                        'zypper', '--non-interactive',
                        'remove', '--clean-deps', '--force-resolution',
                        'azure-li-services'
                    ]
                ),
                call(
                    [
                        'systemctl', 'reset-failed'
                    ]
                )
            ]
