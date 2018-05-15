import io
from pytest import raises
from unittest.mock import (
    MagicMock, patch, call
)
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.units.network import (
    main,
    create_interface_config,
    create_vlan_config
)
from azure_li_services.exceptions import AzureLiNetworkConfigDataException


class TestNetwork(object):
    def setup(self):
        self.config = RuntimeConfig('../data/config.yaml')

    @patch('azure_li_services.units.network.RuntimeConfig')
    @patch('azure_li_services.units.network.Defaults')
    def test_main(self, mock_Defaults, mock_RuntimeConfig):
        mock_RuntimeConfig.return_value = self.config

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            main()
            file_handle = mock_open.return_value.__enter__.return_value
            assert mock_open.call_args_list == [
                call('/etc/sysconfig/network/ifcfg-eth0', 'w'),
                call('/etc/sysconfig/network/ifcfg-eth0.10', 'w'),
                call('/etc/sysconfig/network/ifroute-eth0.10', 'w')
            ]
            assert file_handle.write.call_args_list == [
                call(
                    'BOOTPROTO=static\nBROADCAST=10.250.10.255\n'
                    'NETMASK=255.255.255.0\nSTARTMODE=auto\n'
                ),
                call(
                    'BOOTPROTO=static\nDEVICE=eth0.10\nETHERDEVICE=eth0\n'
                    'IPADDR=10.250.10.51\nNETMASK=255.255.255.0\n'
                    'ONBOOT=yes\nSTARTMODE=auto\nVLAN=yes\nVLAN_ID=10\n'
                ),
                call(
                    'default 10.250.10.1 - eth0.10\n'
                )
            ]

    def test_create_interface_config_raises(self):
        with raises(AzureLiNetworkConfigDataException):
            create_interface_config({})

    def test_create_vlan_config_raises(self):
        with raises(AzureLiNetworkConfigDataException):
            create_vlan_config({})
