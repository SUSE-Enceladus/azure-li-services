from pytest import raises
from unittest.mock import (
    Mock, patch
)
from azure_li_services.units.network import main
from azure_li_services.exceptions import AzureLiNetworkConfigDataException


class TestNetwork(object):
    @patch('azure_li_services.units.network.AzureLiNetworkSetup')
    @patch('azure_li_services.units.network.Defaults.get_config_file')
    def test_main_li_network(
        self, mock_get_config_file, mock_AzureLiNetworkSetup
    ):
        li_network = Mock()
        mock_AzureLiNetworkSetup.return_value = li_network
        mock_get_config_file.return_value = '../data/config.yaml'
        main()
        li_network.create_interface_config.assert_called_once_with()
        li_network.create_vlan_config.assert_called_once_with()
        li_network.create_default_route_config.assert_called_once_with()

    @patch('azure_li_services.units.network.Defaults.get_config_file')
    def test_main_vli_network(self, mock_get_config_file):
        mock_get_config_file.return_value = '../data/config_vli.yaml'
        with raises(AzureLiNetworkConfigDataException):
            main()
