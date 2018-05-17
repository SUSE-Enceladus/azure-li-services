# Copyright (c) 2018 SUSE Linux GmbH.  All rights reserved.
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
from azure_li_services.exceptions import AzureHostedNetworkConfigDataException


class AzureHostedNetworkSetup(object):
    """
    Azure Li/VLi network configuration

    Implements methods to create Network interface configuration files
    """
    def __init__(self, network):
        if (
            'ip' not in network or
            'interface' not in network or
            'subnet_mask' not in network
        ):
            raise AzureHostedNetworkConfigDataException(
                'At least one of {0} missing in {1}'.format(
                    ('ip', 'interface', 'subnet_mask'), network
                )
            )
        self.network = network

    def create_interface_config(self):
        """
        Setup interface configuration
        """
        interface_file = '/etc/sysconfig/network/ifcfg-{0}'.format(
            self.network['interface']
        )
        setup = dedent('''
            BOOTPROTO=static
            BROADCAST={broadcast}
            NETMASK={netmask}
            STARTMODE=auto
        ''').lstrip()
        net4 = ipaddress.IPv4Network(
            '/'.join([self.network['ip'], self.network['subnet_mask']]), False
        )
        with open(interface_file, 'w') as ifcfg:
            ifcfg.write(
                setup.format(
                    broadcast=net4.broadcast_address,
                    netmask=self.network['subnet_mask']
                )
            )

    def create_default_route_config(self):
        """
        Setup default route for interface

        Creates a default route to the gateway ip if specified.
        Takes optional vlan id into account to apply the default
        route to the correct interface
        """
        if 'gateway' in self.network:
            vlan = '.{0}'.format(
                self.network['vlan']
            ) if 'vlan' in self.network else ''
            route_file = '/etc/sysconfig/network/ifroute-{0}{1}'.format(
                self.network['interface'], vlan
            )
            setup = dedent('''
                default {gateway} - {interface}{vlan}
            ''').lstrip()
            with open(route_file, 'w') as ifroute:
                ifroute.write(
                    setup.format(
                        interface=self.network['interface'],
                        vlan=vlan,
                        gateway=self.network['gateway']
                    )
                )

    def create_vlan_config(self):
        """
        Setup vlan configuration on top of interface config
        """
        if 'vlan' not in self.network:
            raise AzureHostedNetworkConfigDataException(
                'vlan id missing in {0}'.format(self.network)
            )
        vlan_file = '/etc/sysconfig/network/ifcfg-{0}.{1}'.format(
            self.network['interface'], self.network['vlan']
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
                    interface=self.network['interface'],
                    vlan=self.network['vlan'],
                    ip=self.network['ip'],
                    netmask=self.network['subnet_mask']
                )
            )

    def create_bridge_config(self):
        """
        Setup bridge configuration on top of interface config
        """
        raise NotImplementedError
