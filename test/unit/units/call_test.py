from unittest.mock import (
    patch, call, Mock
)
from azure_li_services.units.call import main


class TestCall(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.call.Defaults.get_config_file')
    @patch('azure_li_services.units.call.StatusReport')
    def test_main(self, mock_StatusReport, mock_get_config_file, mock_Command_run):
        status = Mock()
        mock_StatusReport.return_value = status
        mock_get_config_file.return_value = '../data/config.yaml'
        main()
        mock_StatusReport.assert_called_once_with('call')
        status.set_success.assert_called_once_with()
        assert mock_Command_run.call_args_list == [
            call(['mount', '--label', 'azconfig', '/mnt']),
            call(['bash', '-c', '/mnt/path/to/executable/file']),
            call(['umount', '/mnt'])
        ]
