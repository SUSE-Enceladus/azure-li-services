import io
from unittest.mock import (
    Mock, MagicMock, patch, call
)
from azure_li_services.units.report import main


class TestReport(object):
    @patch('azure_li_services.units.report.StatusReport')
    def test_main(self, mock_StatusReport):
        report = Mock()
        report.get_state.return_value = False
        mock_StatusReport.return_value = report
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            main()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/issue', 'w'
            )
            assert mock_StatusReport.call_args_list == [
                call('call', init_state=False),
                call('config_lookup', init_state=False),
                call('install', init_state=False),
                call('network', init_state=False),
                call('user', init_state=False)
            ]
            assert file_handle.write.call_args_list == [
                call('\n'),
                call('!!! DEPLOYMENT ERROR !!!'),
                call('\n'),
                call(
                    'For details see: "systemctl status '
                    'azure-li-call azure-li-config-lookup '
                    'azure-li-install azure-li-network azure-li-user"'
                ),
                call('\n'),
                call('\n')
            ]
