from unittest.mock import (
    patch, call
)
from azure_li_services.units.call import main


class TestCall(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.call.Defaults.get_config_file')
    def test_main(self, mock_get_config_file, mock_Command_run):
        mock_get_config_file.return_value = '../data/config.yaml'
        main()
        assert mock_Command_run.call_args_list == [
            call(['mount', '--label', 'azconfig', '/mnt']),
            call(['bash', '-c', '/mnt/path/to/executable/file']),
            call(['umount', '/mnt'])
        ]
