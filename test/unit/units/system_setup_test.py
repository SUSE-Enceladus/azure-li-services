import io
from unittest.mock import (
    patch, Mock, MagicMock, call
)
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.units.system_setup import main


class TestSystemSetup(object):
    def setup(self):
        self.config = RuntimeConfig('../data/config.yaml')

    @patch('os.chmod')
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.system_setup.Defaults.get_config_file')
    @patch('azure_li_services.units.system_setup.RuntimeConfig')
    @patch('azure_li_services.units.system_setup.StatusReport')
    def test_main(
        self, mock_StatusReport, mock_RuntimConfig, mock_get_config_file,
        mock_Command_run, mock_os_chmod
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        mock_RuntimConfig.return_value = self.config
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            main()
            mock_StatusReport.assert_called_once_with('system_setup')
            status.set_success.assert_called_once_with()
            assert mock_open.call_args_list == [
                call('/sys/kernel/mm/ksm/run', 'w'),
                call('/etc/init.d/boot.local', 'a'),
                call('/etc/init.d/boot.local', 'a')
            ]
            assert file_handle.write.call_args_list == [
                call('0\n'),
                call('echo 0 > /sys/kernel/mm/ksm/run\n'),
                call('cpupower frequency-set -g performance\n'),
                call('cpupower set -b 0\n')
            ]
            assert mock_Command_run.call_args_list == [
                call(['hostnamectl', 'set-hostname', 'azure']),
                call(['cpupower', 'frequency-set', '-g', 'performance']),
                call(['cpupower', 'set', '-b', '0'])
            ]
            assert mock_os_chmod.call_args_list == [
                call('/etc/init.d/boot.local', 0o755),
                call('/etc/init.d/boot.local', 0o755)
            ]
