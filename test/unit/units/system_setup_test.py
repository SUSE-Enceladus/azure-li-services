import io
import os
from textwrap import dedent
from unittest.mock import (
    patch, Mock, MagicMock, call
)
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.instance_type import InstanceType
from azure_li_services.units.system_setup import main

import azure_li_services.units.system_setup as system_setup


class TestSystemSetup(object):
    def setup(self):
        self.config = RuntimeConfig('../data/config.yaml')

    @patch.object(system_setup, 'set_hostname')
    @patch.object(system_setup, 'set_kdump_service')
    @patch.object(system_setup, 'set_kernel_samepage_merging_mode')
    @patch.object(system_setup, 'set_energy_performance_settings')
    @patch.object(system_setup, 'set_saptune_service')
    @patch.object(system_setup, 'set_reboot_intervention')
    @patch.object(system_setup.Defaults, 'get_config_file')
    @patch.object(system_setup, 'RuntimeConfig')
    @patch.object(system_setup, 'StatusReport')
    def test_main(
        self, mock_StatusReport, mock_RuntimConfig, mock_get_config_file,
        mock_set_reboot_intervention,
        mock_set_saptune_service,
        mock_set_energy_performance_settings,
        mock_set_kernel_samepage_merging_mode,
        mock_set_kdump_service, mock_set_hostname
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        mock_RuntimConfig.return_value = self.config
        main()
        mock_set_hostname.assert_called_once_with('azure')
        mock_set_kdump_service.assert_called_once_with(160, 80, status)
        mock_set_kernel_samepage_merging_mode.assert_called_once_with()
        mock_set_energy_performance_settings.assert_called_once_with()
        mock_set_saptune_service.assert_called_once_with()
        mock_StatusReport.assert_called_once_with('system_setup')
        status.set_success.assert_called_once_with()

        self.config.get_instance_type = Mock(
            return_value=InstanceType.vli
        )
        main()
        mock_set_reboot_intervention.assert_called_once_with()

    @patch('azure_li_services.command.Command.run')
    def test_set_hostname(self, mock_Command_run):
        system_setup.set_hostname('azure')
        mock_Command_run.assert_called_once_with(
            ['hostnamectl', 'set-hostname', 'azure']
        )

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
            system_setup.set_kdump_service(None, None, status)
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
            call(['systemctl', 'enable', 'tuned']),
            call(['systemctl', 'start', 'tuned']),
            call(['saptune', 'daemon', 'start']),
            call(['saptune', 'solution', 'apply', 'HANA']),
        ]

    @patch('os.path.exists')
    def test_set_reboot_intervention(self, mock_exists):
        mock_exists.return_value = True
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            system_setup.set_reboot_intervention()
            mock_open.assert_called_once_with('/boot/efi/startup.nsh', 'w')
            assert file_handle.write.call_args_list == [
                call('fs0:\\efi\\sles_sap\\grubx64.efi\n')
            ]
