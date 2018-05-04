import os

from unittest.mock import (
    patch,
    Mock
)
from pytest import raises
from collections import namedtuple

from azure_li_services.command import Command

from azure_li_services.exceptions import (
    AzureLiCommandException,
    AzureLiCommandNotFoundException
)


class TestCommand(object):
    @patch('azure_li_services.path.Path.which')
    @patch('subprocess.Popen')
    def test_run_raises_error(self, mock_popen, mock_which):
        mock_which.return_value = 'command'
        mock_process = Mock()
        mock_process.communicate = Mock(
            return_value=[str.encode('stdout'), str.encode('stderr')]
        )
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        with raises(AzureLiCommandException):
            Command.run(['command', 'args'])

    @patch('azure_li_services.path.Path.which')
    @patch('subprocess.Popen')
    def test_run_failure(self, mock_popen, mock_which):
        mock_which.return_value = 'command'
        mock_popen.side_effect = AzureLiCommandException('Run failure')
        with raises(AzureLiCommandException):
            Command.run(['command', 'args'])

    def test_run_invalid_environment(self):
        with raises(AzureLiCommandNotFoundException):
            Command.run(['command', 'args'], {'HOME': '/root'})

    @patch('azure_li_services.path.Path.which')
    @patch('subprocess.Popen')
    def test_run_does_not_raise_error(self, mock_popen, mock_which):
        mock_which.return_value = 'command'
        mock_process = Mock()
        mock_process.communicate = Mock(
            return_value=[str.encode('stdout'), str.encode('')]
        )
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        result = Command.run(['command', 'args'], os.environ, False)
        assert result.error == '(no output on stderr)'
        assert result.output == 'stdout'
        mock_process.communicate = Mock(
            return_value=[str.encode(''), str.encode('stderr')]
        )
        result = Command.run(['command', 'args'], os.environ, False)
        assert result.error == 'stderr'
        assert result.output == '(no output on stdout)'

    @patch('azure_li_services.path.Path.which')
    def test_run_does_not_raise_error_if_command_not_found(self, mock_which):
        mock_which.return_value = None
        result = Command.run(['command', 'args'], os.environ, False)
        assert result.error is None
        assert result.output is None
        assert result.returncode == -1

    @patch('os.access')
    @patch('os.path.exists')
    @patch('subprocess.Popen')
    def test_run(self, mock_popen, mock_exists, mock_access):
        mock_exists.return_value = True
        command_run = namedtuple(
            'command', ['output', 'error', 'returncode']
        )
        run_result = command_run(
            output='stdout',
            error='stderr',
            returncode=0
        )
        mock_process = Mock()
        mock_process.communicate = Mock(
            return_value=[str.encode('stdout'), str.encode('stderr')]
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        mock_access.return_value = True
        assert Command.run(['command', 'args']) == run_result

    def test_run_command_does_not_exist(self):
        with raises(AzureLiCommandNotFoundException):
            Command.run(['does-not-exist'])

    def test_call_command_does_not_exist(self):
        with raises(AzureLiCommandNotFoundException):
            Command.call(['does-not-exist'], os.environ)

    @patch('azure_li_services.path.Path.which')
    @patch('subprocess.Popen')
    @patch('select.select')
    def test_call(self, mock_select, mock_popen, mock_which):
        mock_which.return_value = 'command'
        mock_select.return_value = [True, False, False]
        mock_process = Mock()
        mock_popen.return_value = mock_process
        call = Command.call(['command', 'args'])
        assert call.output_available()
        assert call.error_available()
        assert call.output == mock_process.stdout
        assert call.error == mock_process.stderr
        assert call.process == mock_process

    @patch('azure_li_services.path.Path.which')
    @patch('subprocess.Popen')
    def test_call_failure(self, mock_popen, mock_which):
        mock_which.return_value = 'command'
        mock_popen.side_effect = AzureLiCommandException('Call failure')
        with raises(AzureLiCommandException):
            Command.call(['command', 'args'])
