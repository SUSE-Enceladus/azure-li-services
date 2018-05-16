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
# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.network import AzureLiNetworkSetup
from azure_li_services.instance_type import InstanceType

from azure_li_services.exceptions import AzureLiNetworkConfigDataException


def main():
    """
    Azure Li/Vli network setup

    Creates network configuration files to successfully start the
    network in the scope of an Azure Li/Vli instance
    """
    config = RuntimeConfig(Defaults.get_config_file())
    network_config = config.get_network_config()
    instance_type = config.get_instance_type()
    if network_config:
        if instance_type == InstanceType.li:
            for network in network_config:
                li_network = AzureLiNetworkSetup(network)
                li_network.create_interface_config()
                li_network.create_vlan_config()
                li_network.create_default_route_config()
        else:
            raise AzureLiNetworkConfigDataException(
                'No idea how to setup network for Instance Type: {0}'.format(
                    instance_type
                )
            )
