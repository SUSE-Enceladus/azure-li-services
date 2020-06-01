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
import os
import ipaddress
from textwrap import dedent


class AzureHostedNetworkSetup(object):
    """
    Azure Li/VLi network configuration

    Implements methods to create Network interface configuration files
    """
    def __init__(self, network):
        self.network = network
        self._is_hosts_updated = False

    def create_interface_config(self):
        """
        Setup interface configuration
        """
        if 'vlan' in self.network or 'bonding_slaves' in self.network:
            return
        interface_file = '/etc/sysconfig/network/ifcfg-{0}'.format(
            self.network['interface']
        )
        setup = dedent('''
            BOOTPROTO=static
            STARTMODE=auto
        ''').lstrip()
        with open(interface_file, 'w') as ifcfg:
            ifcfg.write(setup)
            if 'ip' in self.network and 'subnet_mask' in self.network:
                net4 = ipaddress.IPv4Network(
                    '/'.join(
                        [self.network['ip'], self.network['subnet_mask']]
                    ), False
                )
                ifcfg.write(
                    'BROADCAST={0}{1}'.format(
                        net4.broadcast_address, os.linesep
                    )
                )
                ifcfg.write(
                    'NETMASK={0}{1}'.format(
                        self.network['subnet_mask'], os.linesep
                    )
                )
                ifcfg.write(
                    'IPADDR={0}{1}'.format(self.network['ip'], os.linesep)
                )
            if 'mtu' in self.network:
                ifcfg.write(
                    'MTU={0}{1}'.format(self.network['mtu'], os.linesep)
                )

    def create_default_route_config(self):
        """
        Setup default route for interface

        Creates a default route to the gateway ip if specified.
        Takes optional vlan id into account to apply the default
        route to the correct interface
        """
        if 'gateway' in self.network:
            interface = 'vlan{0}'.format(
                self.network['vlan']
            ) if 'vlan' in self.network else self.network['interface']
            route_file = '/etc/sysconfig/network/ifroute-{0}'.format(
                interface
            )
            setup = dedent('''
                default {gateway} - {interface}
            ''').lstrip()
            with open(route_file, 'w') as ifroute:
                ifroute.write(
                    setup.format(
                        interface=interface,
                        gateway=self.network['gateway']
                    )
                )

    def create_vlan_config(self):
        """
        Setup vlan configuration on top of interface config
        """
        if 'vlan' not in self.network:
            return
        vlan_file = '/etc/sysconfig/network/ifcfg-vlan{0}'.format(
            self.network['vlan']
        )
        setup = dedent('''
            BOOTPROTO=static
            ETHERDEVICE={interface}
            IPADDR={ip}
            NETMASK={netmask}
            STARTMODE=auto
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
            if 'vlan_mtu' in self.network:
                ifcfg_vlan.write(
                    'MTU={0}{1}'.format(self.network['vlan_mtu'], os.linesep)
                )

    def create_bond_config(self):
        """
        Setup bond configuraton on top of interface config
        """
        if 'bonding_slaves' not in self.network:
            return
        bond_file = '/etc/sysconfig/network/ifcfg-{0}'.format(
            self.network['interface']
        )
        setup = dedent('''
            BOOTPROTO=none
            STARTMODE=auto
            BONDING_MASTER=yes
        ''').lstrip()
        with open(bond_file, 'w') as ifcfg_bond:
            ifcfg_bond.write(
                setup.format(interface=self.network['interface'])
            )
            if 'vlan' not in self.network:
                # bond takes IP setup if present and no vlan is requested
                if 'ip' in self.network:
                    ifcfg_bond.write(
                        'IPADDR={0}{1}'.format(self.network['ip'], os.linesep)
                    )
                if 'subnet_mask' in self.network:
                    ifcfg_bond.write(
                        'NETMASK={0}{1}'.format(
                            self.network['subnet_mask'], os.linesep
                        )
                    )
            if 'mtu' in self.network:
                ifcfg_bond.write(
                    'MTU={0}{1}'.format(self.network['mtu'], os.linesep)
                )
            if 'bonding_options' in self.network:
                ifcfg_bond.write(
                    'BONDING_MODULE_OPTS="{0}"{1}'.format(
                        ' '.join(self.network['bonding_options']), os.linesep
                    )
                )
            slave_index = 0
            for bonding_slave in self.network['bonding_slaves']:
                ifcfg_bond.write(
                    'BONDING_SLAVE{0}={1}{2}'.format(
                        slave_index, bonding_slave, os.linesep
                    )
                )
                slave_index += 1

    def create_bridge_config(self):
        """
        Setup bridge configuration on top of interface config
        """
        raise NotImplementedError

    def update_hosts(self, hostname):
        """Set up hostname for testing purposes."""
        if self._is_hosts_updated:
            return
        if 'vlan' not in self.network:
            return
        if str(self.network['vlan'])[-1] == '0' and self.network['vlan_mtu'] == 1500:
            if 'ip' in self.network:
                hosts_file = '/etc/hosts'
                setup = dedent('''
                    {ip} {hostname}.example.com {repeat_hostname}
                ''').lstrip()
                with open(hosts_file, 'w') as etc_hosts:
                    etc_hosts.write(
                        setup.format(ip=self.network['ip'],
                                     hostname=hostname,
                                     repeat_hostname=hostname)
                    )
                    self._is_hosts_updated = True
