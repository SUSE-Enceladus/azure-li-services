import humanfriendly
from pytest import raises
from unittest.mock import (
    patch, Mock
)
from azure_li_services.units.machine_constraints import main
from azure_li_services.exceptions import AzureHostedException


class TestMachineConstraints(object):
    @patch('azure_li_services.logger.Logger.setup')
    @patch('azure_li_services.units.machine_constraints.Defaults.get_config_file')
    @patch('azure_li_services.units.machine_constraints.StatusReport')
    @patch('multiprocessing.cpu_count')
    @patch('azure_li_services.units.machine_constraints.virtual_memory')
    def test_main(
        self, mock_virtual_memory, mock_cpu_count,
        mock_StatusReport, mock_get_config_file, mock_logger_setup
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        mock_get_config_file.return_value = '../data/config.yaml'
        mock_cpu_count.return_value = 42
        existing_memory = Mock()
        existing_memory.total = humanfriendly.parse_size('20tb', binary=True)
        mock_virtual_memory.return_value = existing_memory
        main()
        mock_StatusReport.assert_called_once_with('machine_constraints')
        status.set_success.assert_called_once_with()
        mock_cpu_count.return_value = 2
        with raises(AzureHostedException):
            main()
        mock_cpu_count.return_value = 42
        existing_memory.total = humanfriendly.parse_size('1gb', binary=True)
        with raises(AzureHostedException):
            main()
