from unittest.mock import patch
from azure_li_services.units.cleanup import main


class TestCleanup(object):
    @patch('azure_li_services.command.Command.run')
    def test_main(self, mock_Command_run):
        main()
        mock_Command_run.assert_called_once_with(
            [
                'zypper', '--non-interactive',
                'remove', '--clean-deps', '--force-resolution',
                'azure-li-services'
            ]
        )
