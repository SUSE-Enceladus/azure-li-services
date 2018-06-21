from unittest.mock import (
    patch, Mock
)
from azure_li_services.units.system_setup import main


class TestSystemSetup(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.system_setup.Defaults.get_config_file')
    @patch('azure_li_services.units.system_setup.StatusReport')
    def test_main(
        self, mock_StatusReport, mock_get_config_file, mock_Command_run
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        mock_get_config_file.return_value = '../data/config.yaml'
        main()
        mock_StatusReport.assert_called_once_with('system_setup')
        status.set_success.assert_called_once_with()
        mock_Command_run.assert_called_once_with(
            ['hostnamectl', 'set-hostname', 'azure']
        )
