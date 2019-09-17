from unittest.mock import (
    patch, call, Mock
)
from azure_li_services.units.call import main


class TestCall(object):
    @patch('azure_li_services.logger.Logger.setup')
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.call.Defaults.get_config_file')
    @patch('azure_li_services.units.call.StatusReport')
    @patch('azure_li_services.defaults.Defaults.mount_config_source')
    def test_main(
        self, mock_mount_config_source, mock_StatusReport,
        mock_get_config_file, mock_Command_run, mock_logger_setup
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        mock_get_config_file.return_value = '../data/config.yaml'
        main()
        mock_StatusReport.assert_called_once_with('call')
        status.set_success.assert_called_once_with()
        assert mock_Command_run.call_args_list == [
            call(
                [
                    'bash', '-c', '{0}/path/to/executable/file'.format(
                        mock_mount_config_source.return_value.location
                    )
                ]
            )
        ]
