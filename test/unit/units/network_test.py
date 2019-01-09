from pytest import raises
from unittest.mock import (
    Mock, patch
)
from azure_li_services.units.network import main
from azure_li_services.exceptions import (
    AzureHostedException,
    AzureHostedNetworkConfigDataException
)


class TestNetwork(object):
    @patch('azure_li_services.units.network.AzureHostedNetworkSetup')
    @patch('azure_li_services.units.network.Defaults.get_config_file')
    @patch('azure_li_services.units.network.StatusReport')
    def test_main_li_vli_network(
        self, mock_StatusReport, mock_get_config_file,
        mock_AzureHostedNetworkSetup
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        li_network = Mock()
        mock_AzureHostedNetworkSetup.return_value = li_network
        mock_get_config_file.return_value = '../data/config.yaml'
        main()
        mock_StatusReport.assert_called_once_with('network')
        status.set_success.assert_called_once_with()
        li_network.create_interface_config.assert_called_once_with()
        li_network.create_vlan_config.assert_called_once_with()
        li_network.create_default_route_config.assert_called_once_with()
        mock_AzureHostedNetworkSetup.side_effect = Exception
        with raises(AzureHostedException):
            main()

    @patch('azure_li_services.units.network.Defaults.get_config_file')
    @patch('azure_li_services.units.network.StatusReport')
    def test_main_vli_gen3_network(
        self, mock_StatusReport, mock_get_config_file
    ):
        mock_get_config_file.return_value = '../data/config_vli_gen3.yaml'
        with raises(AzureHostedNetworkConfigDataException):
            main()
