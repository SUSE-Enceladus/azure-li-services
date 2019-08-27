import io
from pytest import raises
from unittest.mock import (
    MagicMock, patch, call
)
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.network import AzureHostedNetworkSetup


class TestAzureHostedNetworkSetup(object):
    def setup(self):
        config_nic = RuntimeConfig('../data/config-net.yaml')
        config_vlan = RuntimeConfig('../data/config-net-vlan.yaml')
        config_bond = RuntimeConfig('../data/config-net-bond.yaml')
        config_bond_vlan = RuntimeConfig('../data/config-net-bond-vlan.yaml')
        config_vlan_bond = RuntimeConfig('../data/config-net-vlan-bond.yaml')

        self.network_config = config_nic.get_network_config()
        self.network_config_vlan = config_vlan.get_network_config()
        self.network_config_bond = config_bond.get_network_config()
        self.network_config_bond_vlan = config_bond_vlan.get_network_config()
        self.network_config_vlan_bond = config_vlan_bond.get_network_config()

    def test_create_default_route_config(self):
        network = AzureHostedNetworkSetup(self.network_config[0])
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            network.create_default_route_config()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/sysconfig/network/ifroute-eth0', 'w'
            )
            file_handle.write.assert_called_once_with(
                'default 10.250.10.1 - eth0\n'
            )

    def test_create_interface_config(self):
        network = AzureHostedNetworkSetup(self.network_config[0])
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            network.create_interface_config()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/sysconfig/network/ifcfg-eth0', 'w'
            )
            assert file_handle.write.call_args_list == [
                call(
                    'BOOTPROTO=static\n'
                    'STARTMODE=auto\n'
                ),
                call(
                    'BROADCAST=10.250.10.255\n'
                ),
                call(
                    'NETMASK=255.255.255.0\n'
                ),
                call('IPADDR=10.250.10.51\n'),
                call('MTU=9000\n')
            ]

    def test_create_vlan_config(self):
        network = AzureHostedNetworkSetup(self.network_config_vlan[0])
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            network.create_vlan_config()
            file_handle = mock_open.return_value.__enter__.return_value
            mock_open.assert_called_once_with(
                '/etc/sysconfig/network/ifcfg-vlan10', 'w'
            )
            assert file_handle.write.call_args_list == [
                call(
                    'BOOTPROTO=static\n'
                    'ETHERDEVICE=eth0\n'
                    'IPADDR=10.250.10.51\n'
                    'NETMASK=255.255.255.0\n'
                    'STARTMODE=auto\n'
                    'VLAN_ID=10\n'
                ),
                call('MTU=1500\n')
            ]

    def test_create_vlan_config_skipped_on_missing_id(self):
        network = AzureHostedNetworkSetup(self.network_config[0])
        with patch('builtins.open', create=True) as mock_open:
            network.create_vlan_config()
            assert mock_open.called is False

    def test_create_bridge_config(self):
        network = AzureHostedNetworkSetup(self.network_config[0])
        with raises(NotImplementedError):
            network.create_bridge_config()

    def test_create_bond_config(self):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            for network_config in self.network_config_bond:
                network = AzureHostedNetworkSetup(network_config)
                network.create_interface_config()
                network.create_bond_config()
            assert file_handle.write.call_args_list == [
                # eth0
                call('BOOTPROTO=static\nSTARTMODE=auto\n'),
                # eth1
                call('BOOTPROTO=static\nSTARTMODE=auto\n'),
                # bond0
                call(
                    'BOOTPROTO=none\n'
                    'STARTMODE=auto\n'
                    'BONDING_MASTER=yes\n'
                ),
                call('IPADDR=10.250.10.51\n'),
                call('NETMASK=255.255.255.0\n'),
                call('BONDING_MODULE_OPTS="opt=val"\n'),
                call('BONDING_SLAVE0=eth0\n'),
                call('BONDING_SLAVE1=eth1\n')
            ]
            assert mock_open.call_args_list == [
                call('/etc/sysconfig/network/ifcfg-eth0', 'w'),
                call('/etc/sysconfig/network/ifcfg-eth1', 'w'),
                call('/etc/sysconfig/network/ifcfg-bond0', 'w')
            ]

    def test_create_bond_vlan_config(self):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            for network_config in self.network_config_bond_vlan:
                network = AzureHostedNetworkSetup(network_config)
                network.create_interface_config()
                network.create_vlan_config()
                network.create_bond_config()
                network.create_default_route_config()
            assert mock_open.call_args_list == [
                call('/etc/sysconfig/network/ifcfg-eth3', 'w'),
                call('/etc/sysconfig/network/ifcfg-eth4', 'w'),
                call('/etc/sysconfig/network/ifcfg-eth5', 'w'),
                call('/etc/sysconfig/network/ifcfg-eth6', 'w'),
                call('/etc/sysconfig/network/ifcfg-bond0', 'w'),
                call('/etc/sysconfig/network/ifcfg-bond1', 'w'),
                call('/etc/sysconfig/network/ifcfg-vlan250', 'w'),
                call('/etc/sysconfig/network/ifroute-vlan250', 'w'),
                call('/etc/sysconfig/network/ifcfg-vlan251', 'w'),
                call('/etc/sysconfig/network/ifcfg-vlan253', 'w'),
                call('/etc/sysconfig/network/ifcfg-vlan252', 'w')
            ]
            assert file_handle.write.call_args_list == [
                # eth3-6
                call('BOOTPROTO=static\nSTARTMODE=auto\n'),
                call('BOOTPROTO=static\nSTARTMODE=auto\n'),
                call('BOOTPROTO=static\nSTARTMODE=auto\n'),
                call('BOOTPROTO=static\nSTARTMODE=auto\n'),
                # bond0-1
                call(
                    'BOOTPROTO=none\n'
                    'STARTMODE=auto\n'
                    'BONDING_MASTER=yes\n'
                ),
                call('BONDING_MODULE_OPTS="mode=active-backup miimon=100"\n'),
                call('BONDING_SLAVE0=eth3\n'),
                call('BONDING_SLAVE1=eth6\n'),
                call(
                    'BOOTPROTO=none\n'
                    'STARTMODE=auto\n'
                    'BONDING_MASTER=yes\n'
                ),
                call('BONDING_MODULE_OPTS="mode=active-backup miimon=100"\n'),
                call('BONDING_SLAVE0=eth4\n'),
                call('BONDING_SLAVE1=eth5\n'),
                # vlan250-253
                call(
                    'BOOTPROTO=static\n'
                    'ETHERDEVICE=bond0\n'
                    'IPADDR=10.60.0.35\n'
                    'NETMASK=255.255.255.0\n'
                    'STARTMODE=auto\n'
                    'VLAN_ID=250\n'
                ),
                call('MTU=9000\n'),
                call('default 10.60.0.1 - vlan250\n'),
                call(
                    'BOOTPROTO=static\n'
                    'ETHERDEVICE=bond0\n'
                    'IPADDR=10.20.251.150\n'
                    'NETMASK=255.255.255.0\n'
                    'STARTMODE=auto\n'
                    'VLAN_ID=251\n'
                ),
                call('MTU=9000\n'),
                call(
                    'BOOTPROTO=static\n'
                    'ETHERDEVICE=bond0\n'
                    'IPADDR=10.20.253.150\n'
                    'NETMASK=255.255.255.0\n'
                    'STARTMODE=auto\n'
                    'VLAN_ID=253\n'
                ),
                call('MTU=9000\n'),
                call(
                    'BOOTPROTO=static\n'
                    'ETHERDEVICE=bond1\n'
                    'IPADDR=10.20.252.150\n'
                    'NETMASK=255.255.255.0\n'
                    'STARTMODE=auto\n'
                    'VLAN_ID=252\n'
                ),
                call('MTU=9000\n')
            ]

    def test_create_vlan_bond_config(self):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            for network_config in self.network_config_vlan_bond:
                network = AzureHostedNetworkSetup(network_config)
                network.create_interface_config()
                network.create_vlan_config()
                network.create_bond_config()
            assert file_handle.write.call_args_list == [
                # eth0
                call(
                    'BOOTPROTO=static\n'
                    'STARTMODE=auto\n'
                ),
                # eth1
                call(
                    'BOOTPROTO=static\n'
                    'STARTMODE=auto\n'
                ),
                # vlan interface bond0.10
                call(
                    'BOOTPROTO=static\n'
                    'ETHERDEVICE=bond0\n'
                    'IPADDR=10.250.10.51\n'
                    'NETMASK=255.255.255.0\n'
                    'STARTMODE=auto\n'
                    'VLAN_ID=10\n'
                ),
                call('MTU=1500\n'),
                # bond0
                call(
                    'BOOTPROTO=none\n'
                    'STARTMODE=auto\n'
                    'BONDING_MASTER=yes\n'
                ),
                call('MTU=9000\n'),
                call('BONDING_MODULE_OPTS="opt=value"\n'),
                call('BONDING_SLAVE0=eth0\n'),
                call('BONDING_SLAVE1=eth1\n')
            ]
            assert mock_open.call_args_list == [
                call('/etc/sysconfig/network/ifcfg-eth0', 'w'),
                call('/etc/sysconfig/network/ifcfg-eth1', 'w'),
                call('/etc/sysconfig/network/ifcfg-vlan10', 'w'),
                call('/etc/sysconfig/network/ifcfg-bond0', 'w')
            ]
