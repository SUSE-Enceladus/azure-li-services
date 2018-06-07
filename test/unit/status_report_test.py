import io
from unittest.mock import (
    MagicMock, patch, call
)

from azure_li_services.status_report import StatusReport


class TestStatusReport(object):
    @patch('os.path.exists')
    @patch('azure_li_services.status_report.Path.create')
    def setup(self, mock_Path_create, mock_exists):
        mock_exists.return_value = False
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            self.report = StatusReport('some_service')
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/azure_li_services/some_service.report.yaml', 'w'
            )
            assert file_handle.write.call_args_list == [
                call('some_service'),
                call(':'),
                call('\n'),
                call('  '),
                call('success'),
                call(':'),
                call(' '),
                call('false'),
                call('\n')
            ]

    def test_set_success(self):
        with patch('builtins.open', create=True) as mock_open:
            self.report.set_success()
            mock_open.assert_called_once_with(
                '/etc/azure_li_services/some_service.report.yaml', 'w'
            )
            assert self.report.status['some_service']['success'] is True

    def test_set_failed(self):
        with patch('builtins.open', create=True) as mock_open:
            self.report.set_failed()
            mock_open.assert_called_once_with(
                '/etc/azure_li_services/some_service.report.yaml', 'w'
            )
            assert self.report.status['some_service']['success'] is False

    def test_load(self):
        self.report.status_file = '../data/some_service.report.yaml'
        result = self.report.load()
        assert result['some_service']['success'] is True
