import io
import os
from pytest import raises
from textwrap import dedent
from unittest.mock import (
    patch, Mock, MagicMock, call
)
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.instance_type import InstanceType
from azure_li_services.units.system_setup import main

import azure_li_services.units.system_setup as system_setup

from azure_li_services.exceptions import (
    AzureHostedException,
    AzureHostedCommandOutputException
)


class TestSystemSetup(object):
    def setup(self):
        self.config = RuntimeConfig('../data/config.yaml')

    @patch('azure_li_services.logger.Logger.setup')
    @patch.object(system_setup, 'enable_extra_kernel_modules')
    @patch.object(system_setup, 'set_hostname')
    @patch.object(system_setup, 'set_stonith_service')
    @patch.object(system_setup, 'set_kdump_service')
    @patch.object(system_setup, 'set_kernel_samepage_merging_mode')
    @patch.object(system_setup, 'set_energy_performance_settings')
    @patch.object(system_setup, 'set_saptune_service')
    @patch.object(system_setup.Defaults, 'get_config_file')
    @patch.object(system_setup, 'RuntimeConfig')
    @patch.object(system_setup, 'StatusReport')
    def test_main(
        self, mock_StatusReport, mock_RuntimConfig, mock_get_config_file,
        mock_set_saptune_service,
        mock_set_energy_performance_settings,
        mock_set_kernel_samepage_merging_mode,
        mock_set_kdump_service, mock_set_stonith_service,
        mock_set_hostname, mock_extra_modules,
        mock_logger_setup
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        mock_RuntimConfig.return_value = self.config
        main()
        mock_set_hostname.assert_called_once_with('azure')
        mock_set_stonith_service.assert_called_once_with(
            {'initiatorname': 't090xyzzysid4', 'ip': '192.168.100.20'}
        )
        mock_extra_modules.assert_called_once()
        mock_set_kdump_service.assert_called_once_with(
            {
                'activate': True,
                'crash_kernel_low': 80,
                'crash_kernel_high': 160
            }, status
        )
        mock_set_kernel_samepage_merging_mode.assert_called_once_with()
        mock_set_energy_performance_settings.assert_called_once_with()
        mock_set_saptune_service.assert_called_once_with()
        mock_StatusReport.assert_called_once_with('system_setup')
        status.set_success.assert_called_once_with()

        self.config.get_instance_type = Mock(
            return_value=InstanceType.vli
        )
        main()

        mock_set_hostname.side_effect = Exception
        with raises(AzureHostedException):
            main()

        mock_set_hostname.reset_mock()
        mock_set_stonith_service.side_effect = Exception
        with raises(AzureHostedException):
            main()

        mock_set_stonith_service.reset_mock()
        mock_set_kdump_service.side_effect = Exception
        with raises(AzureHostedException):
            main()

        mock_set_kdump_service.reset_mock()
        mock_set_kernel_samepage_merging_mode.side_effect = Exception
        with raises(AzureHostedException):
            main()

        mock_set_kernel_samepage_merging_mode.reset_mock()
        mock_set_energy_performance_settings.side_effect = Exception
        with raises(AzureHostedException):
            main()

        mock_set_energy_performance_settings.reset_mock()
        mock_set_saptune_service.side_effect = Exception
        with raises(AzureHostedException):
            main()

    @patch('azure_li_services.command.Command.run')
    def test_set_hostname(self, mock_Command_run):
        system_setup.set_hostname('azure')
        mock_Command_run.assert_called_once_with(
            ['hostnamectl', 'set-hostname', 'azure']
        )
        mock_Command_run.side_effect = Exception

    @patch('os.chmod')
    def test_set_kernel_samepage_merging_mode(self, mock_os_chmod):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            system_setup.set_kernel_samepage_merging_mode()
            assert mock_open.call_args_list == [
                call('/sys/kernel/mm/ksm/run', 'w'),
                call('/etc/init.d/boot.local', 'a')
            ]
            assert file_handle.write.call_args_list == [
                call('0\n'),
                call('echo 0 > /sys/kernel/mm/ksm/run\n'),
            ]
            mock_os_chmod.assert_called_once_with(
                '/etc/init.d/boot.local', 0o755
            )

    @patch('os.chmod')
    @patch('azure_li_services.command.Command.run')
    def test_set_energy_performance_settings(
        self, mock_Command_run, mock_os_chmod
    ):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            system_setup.set_energy_performance_settings()
            mock_open.assert_called_once_with(
                '/etc/init.d/boot.local', 'a'
            )
            assert file_handle.write.call_args_list == [
                call('cpupower frequency-set -g performance\n'),
                call('cpupower set -b 0\n')
            ]
            assert mock_Command_run.call_args_list == [
                call(['cpupower', 'frequency-set', '-g', 'performance']),
                call(['cpupower', 'set', '-b', '0'])
            ]
            mock_os_chmod.assert_called_once_with(
                '/etc/init.d/boot.local', 0o755
            )

    @patch('azure_li_services.command.Command.run')
    def test_set_kdump_service_disabled(self, mock_Command_run):
        with patch('builtins.open', create=True) as mock_open:
            system_setup.set_kdump_service({'activate': False}, Mock())
            assert mock_open.called is False
            assert mock_Command_run.called is False

    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.system_setup.virtual_memory')
    def test_set_kdump_service(self, mock_virtual_memory, mock_Command_run):
        memory = Mock()
        memory.total = 2216746782720
        mock_virtual_memory.return_value = memory
        kdumptool_call = Mock()
        kdumptool_call.output = dedent('''
            Total: 16308
            Low: 72
            High: 123
            MinLow: 72
            MaxLow: 2455
            MinHigh: 0
            MaxHigh: 13824
        ''').strip() + os.linesep
        mock_Command_run.return_value = kdumptool_call
        with open('../data/default_grub') as handle:
            grub_defaults_data = handle.read()
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            file_handle.read.return_value = grub_defaults_data
            status = Mock()
            system_setup.set_kdump_service(None, status)
            assert file_handle.write.call_args_list == [
                call(
                    'GRUB_CMDLINE_LINUX_DEFAULT="quiet splash=silent '
                    'crashkernel=246M,high crashkernel=72M,low"\n'
                )
            ]
            assert mock_Command_run.call_args_list == [
                call(['kdumptool', 'calibrate']),
                call(['grub2-mkconfig', '-o', '/boot/grub2/grub.cfg']),
                call(['systemctl', 'restart', 'kdump'])
            ]
            status.set_reboot_required.assert_called_once_with()

    @patch('azure_li_services.command.Command.run')
    def test_set_saptune_service(self, mock_Command_run):
        system_setup.set_saptune_service()
        assert mock_Command_run.call_args_list == [
            call(['saptune', 'daemon', 'start']),
            call(['saptune', 'solution', 'apply', 'HANA'])
        ]

    @patch('azure_li_services.command.Command.run')
    def test_set_stonith_service_discovery_failed(self, mock_Command_run):
        command = Mock
        command.output = 'artificial'
        mock_Command_run.return_value = command
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            file_handle.read.return_value = ''
            with raises(AzureHostedCommandOutputException):
                system_setup.set_stonith_service(
                    {'initiatorname': 't090xyzzysid4', 'ip': '10.20.253.31'}
                )

    @patch('azure_li_services.command.Command.run')
    def test_set_stonith_service(self, mock_Command_run):
        command = Mock
        command.output = os.linesep.join(
            [
                '10.20.253.31:3260,1054 iqn.1992-08.com.netapp:sn.'
                '562892c1030b11e9b8ec00a098d274e4:vs.6',
                '10.20.253.42:3260,1057 iqn.1992-08.com.netapp:sn.'
                '562892c1030b11e9b8ec00a098d274e4:vs.6'
            ]
        )
        mock_Command_run.return_value = command
        with patch('builtins.open', create=True) as mock_open:
            mock_open_initiator = MagicMock(spec=io.IOBase)
            mock_open_iscsi = MagicMock(spec=io.IOBase)
            mock_open_sbd = MagicMock(spec=io.IOBase)

            def open_file(filename, mode):
                if filename == '/etc/iscsi/initiatorname.iscsi':
                    return mock_open_initiator.return_value
                elif filename == '/etc/iscsi/iscsid.conf':
                    return mock_open_iscsi.return_value
                elif filename == '/etc/sysconfig/sbd':
                    return mock_open_sbd.return_value

            mock_open.side_effect = open_file

            file_handle_initiator = \
                mock_open_initiator.return_value.__enter__.return_value
            file_handle_iscsi = \
                mock_open_iscsi.return_value.__enter__.return_value
            file_handle_sbd = \
                mock_open_sbd.return_value.__enter__.return_value

            file_handle_initiator.read.return_value = 'InitiatorName=name'
            file_handle_iscsi.read.return_value = dedent('''
                node.session.timeo.replacement_timeout = 120
                node.startup = manual
            ''')

            system_setup.set_stonith_service(
                {'initiatorname': 't090xyzzysid4', 'ip': '10.20.253.31'}
            )
            assert mock_open.call_args_list == [
                call('/etc/iscsi/initiatorname.iscsi', 'r'),
                call('/etc/iscsi/initiatorname.iscsi', 'w'),
                call('/etc/iscsi/iscsid.conf', 'r'),
                call('/etc/iscsi/iscsid.conf', 'w'),
                call('/etc/sysconfig/sbd', 'w')
            ]
            assert file_handle_initiator.write.call_args_list == [
                call('InitiatorName=iqn.1996-04.de.suse:01:t090xyzzysid4')
            ]
            assert file_handle_iscsi.write.call_args_list == [
                call(dedent('''
                    node.session.timeo.replacement_timeout = 5
                    node.startup = automatic
                '''))
            ]
            assert mock_Command_run.call_args_list == [
                call(
                    [
                        'iscsiadm', '-m', 'discovery', '-t',
                        'st', '-p', '10.20.253.31:3260'
                    ]
                ),
                call(
                    ['iscsiadm', '-m', 'node', '-l']
                ),
                call(
                    ['rescan-scsi-bus.sh']
                ),
                call(
                    ['systemctl', 'restart', 'iscsi']
                ),
                call(
                    ['systemctl', 'restart', 'iscsid']
                ),
                call(
                    ['udevadm', 'settle', '--timeout=30']
                ),
                call(
                    [
                        'sbd', '-d',
                        '/dev/disk/by-path/ip-10.20.253.31:3260-iscsi-iqn.'
                        '1992-08.com.netapp:sn.'
                        '562892c1030b11e9b8ec00a098d274e4:vs.6-lun-0',
                        'create'
                    ]
                ),
                call(
                    [
                        'sbd', '-d',
                        '/dev/disk/by-path/ip-10.20.253.31:3260-iscsi-iqn.'
                        '1992-08.com.netapp:sn.'
                        '562892c1030b11e9b8ec00a098d274e4:vs.6-lun-0',
                        'dump'
                    ]
                )
            ]
            file_handle_sbd.write.assert_called_once_with(
                'SBD_DEVICE="/dev/disk/by-path/ip-10.20.253.31:3260-iscsi-iqn.'
                '1992-08.com.netapp:sn.'
                '562892c1030b11e9b8ec00a098d274e4:vs.6-lun-0"'
            )

    @patch('azure_li_services.command.Command.run')
    def test_load_stonith_needed_modules(
        self, mock_Command_run
    ):
        with patch('builtins.open', create=True) as mock_open:
            mock_open_module_load = MagicMock(spec=io.IOBase)

            def open_file(filename, mode):
                return mock_open_module_load.return_value

            mock_open.side_effect = open_file

            file_handle_module_load = \
                mock_open_module_load.return_value.__enter__.return_value
            system_setup.enable_extra_kernel_modules()
            assert mock_open.call_args_list == [
                call('/etc/modules-load.d/azure-extra-modules.conf', 'w')
            ]
            assert file_handle_module_load.write.call_args_list == [
                call('\nsoftdog')
            ]
            assert mock_Command_run.call_args_list == [
                call(
                    ['modprobe', 'softdog']
                )
            ]
