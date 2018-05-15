# Copyright (c) 2017 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of azure-li-services.
#
# azure-li-services is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# azure-li-services is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with azure-li-services.  If not, see <http://www.gnu.org/licenses/>
#
import ipaddress
from textwrap import dedent

# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.exceptions import AzureLiNetworkConfigDataException


def main():
    """
    Azure Li/Vli network setup

    Creates network configuration files to successfully start the
    network in the scope of an Azure Li/Vli instance
    """
    config = RuntimeConfig(Defaults.get_config_file())
    network_config = config.get_network_config()
    if network_config:
        for network in network_config:
            create_interface_config(network)
            create_vlan_config(network)
            create_interface_default_route(network)


def create_interface_config(network):
    if (
        'ip' not in network or
        'interface' not in network or
        'subnet_mask' not in network
    ):
        raise AzureLiNetworkConfigDataException(
            'At least on of ip, interface or subnet_mask missing in networking'
        )
    interface_file = '/etc/sysconfig/network/ifcfg-{0}'.format(
        network['interface']
    )
    setup = dedent('''
        BOOTPROTO=static
        BROADCAST={broadcast}
        NETMASK={netmask}
        STARTMODE=auto
    ''').lstrip()
    net4 = ipaddress.IPv4Network(
        '/'.join([network['ip'], network['subnet_mask']]), False
    )
    with open(interface_file, 'w') as ifcfg:
        ifcfg.write(
            setup.format(
                broadcast=net4.broadcast_address,
                netmask=network['subnet_mask']
            )
        )


def create_vlan_config(network):
    if 'vlan' not in network:
        raise AzureLiNetworkConfigDataException(
            'vlan missing in networking'
        )
    vlan_file = '/etc/sysconfig/network/ifcfg-{0}.{1}'.format(
        network['interface'], network['vlan']
    )
    setup = dedent('''
        BOOTPROTO=static
        DEVICE={interface}.{vlan}
        ETHERDEVICE={interface}
        IPADDR={ip}
        NETMASK={netmask}
        ONBOOT=yes
        STARTMODE=auto
        VLAN=yes
        VLAN_ID={vlan}
    ''').lstrip()
    with open(vlan_file, 'w') as ifcfg_vlan:
        ifcfg_vlan.write(
            setup.format(
                interface=network['interface'],
                vlan=network['vlan'],
                ip=network['ip'],
                netmask=network['subnet_mask']
            )
        )


def create_interface_default_route(network):
    if 'gateway' in network:
        route_file = '/etc/sysconfig/network/ifroute-{0}.{1}'.format(
            network['interface'], network['vlan']
        )
        setup = dedent('''
            default {gateway} - {interface}.{vlan}
        ''').lstrip()
        with open(route_file, 'w') as ifroute:
            ifroute.write(
                setup.format(
                    interface=network['interface'],
                    vlan=network['vlan'],
                    gateway=network['gateway']
                )
            )
