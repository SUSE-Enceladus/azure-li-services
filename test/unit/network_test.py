import io
from pytest import raises
from unittest.mock import (
    MagicMock, patch
)
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.network import AzureHostedNetworkSetup
from azure_li_services.exceptions import AzureHostedNetworkConfigDataException


class TestAzureHostedNetworkSetup(object):
    def setup(self):
        config = RuntimeConfig('../data/config.yaml')
        self.network = AzureHostedNetworkSetup(config.get_network_config()[0])

    def test_init_raises(self):
        with raises(AzureHostedNetworkConfigDataException):
            AzureHostedNetworkSetup({})

    def test_create_interface_config(self):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            self.network.create_interface_config()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/sysconfig/network/ifcfg-eth0', 'w'
            )
            file_handle.write.assert_called_once_with(
                'BOOTPROTO=static\n'
                'BROADCAST=10.250.10.255\n'
                'NETMASK=255.255.255.0\n'
                'STARTMODE=auto\n'
            )

    def test_create_default_route_config(self):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            self.network.create_default_route_config()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/sysconfig/network/ifroute-eth0.10', 'w'
            )
            file_handle.write.assert_called_once_with(
                'default 10.250.10.1 - eth0.10\n'
            )

    def test_create_vlan_config(self):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            self.network.create_vlan_config()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/sysconfig/network/ifcfg-eth0.10', 'w'
            )
            file_handle.write.assert_called_once_with(
                'BOOTPROTO=static\n'
                'DEVICE=eth0.10\n'
                'ETHERDEVICE=eth0\n'
                'IPADDR=10.250.10.51\n'
                'NETMASK=255.255.255.0\n'
                'ONBOOT=yes\n'
                'STARTMODE=auto\n'
                'VLAN=yes\n'
                'VLAN_ID=10\n'
            )

    def test_create_vlan_config_skipped_on_missing_id(self):
        del self.network.network['vlan']
        with patch('builtins.open', create=True) as mock_open:
            self.network.create_vlan_config()
            assert mock_open.called is False

    def test_create_bridge_config(self):
        with raises(NotImplementedError):
            self.network.create_bridge_config()
