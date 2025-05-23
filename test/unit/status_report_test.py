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
                '/var/lib/azure_li_services/some_service.report.yaml', 'w'
            )
            assert file_handle.write.call_args_list == [
                call('some_service'),
                call(':'),
                call('\n'),
                call('  '),
                call('reboot'),
                call(':'),
                call(' '),
                call('false'),
                call('\n'),
                call('  '),
                call('success'),
                call(':'),
                call(' '),
                call('false'),
                call('\n')
            ]

    @patch('os.path.exists')
    @patch('azure_li_services.status_report.Path.create')
    def setup_method(self, cls, mock_Path_create, mock_exists):
        self.setup()

    def test_set_success(self):
        with patch('builtins.open', create=True) as mock_open:
            self.report.set_success()
            mock_open.assert_called_once_with(
                '/var/lib/azure_li_services/some_service.report.yaml', 'w'
            )
            assert self.report.status['some_service']['success'] is True

    def test_set_failed(self):
        with patch('builtins.open', create=True) as mock_open:
            self.report.set_failed()
            mock_open.assert_called_once_with(
                '/var/lib/azure_li_services/some_service.report.yaml', 'w'
            )
            assert self.report.status['some_service']['success'] is False

    def test_set_reboot_required(self):
        with patch('builtins.open', create=True) as mock_open:
            self.report.set_reboot_required()
            mock_open.assert_called_once_with(
                '/var/lib/azure_li_services/some_service.report.yaml', 'w'
            )
            assert self.report.status['some_service']['reboot'] is True

    def test_get_systemd_service(self):
        assert self.report.get_systemd_service() is None

    def test_load(self):
        self.report.status_file = '../data/some_service.report.yaml'
        self.report.load()
        assert self.report.get_state() is True
        assert self.report.get_reboot() is True
