import io
from unittest.mock import (
    Mock, MagicMock, patch, call
)
from azure_li_services.units.report import main


class TestReport(object):
    @patch('azure_li_services.units.report.Defaults.get_service_reports')
    def test_main(self, mock_get_service_reports):
        report = Mock()
        report.get_systemd_service.return_value = 'service-name'
        report.get_state.return_value = False
        mock_get_service_reports.return_value = [report]
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            main()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/issue', 'w'
            )
            assert file_handle.write.call_args_list == [
                call('\n'),
                call('!!! DEPLOYMENT ERROR !!!'),
                call('\n'),
                call('For details see: "systemctl status -l service-name"'),
                call('\n'),
                call('\n')
            ]
