import io

from unittest.mock import (
    patch, MagicMock
)

from azure_li_services.logger import Logger


class TestLogger:
    def test_setup(self):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            logger = Logger()
            logger.setup()
            mock_open.assert_called_once_with(
                '/var/log/azure-li-services.log', 'a', encoding=None
            )
