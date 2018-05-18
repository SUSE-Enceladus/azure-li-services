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
import yaml

# project
from azure_li_services.instance_type import InstanceType


class RuntimeConfig(object):
    """
    **Implements reading of Azure provided runtime config file**

    The provided config file is a yaml formatted file containing
    information to help with automation of customer installation
    and setup processes for e.g SAP Hana workloads

    Following sections are taken into account by the services
    provided with this project:

    .. code:: yaml
        version: some_version_identifier
        instance_type: LargeInstance

        blade:
          sku: identifier
          cpu: expected_number_of_cpus
          memory: expected_min_size_of_main_memory
          time_server: ip_address_of_time_server
          networking:
            -
              interface: eth0
              vlan: 10
              ip: 10.250.10.51
              gateway: 10.250.10.1
              subnet_mask: 255.255.255.0

        storage:
          -
            device: expected_persistent_device_name
            mount: path_to_mount_this_device
            size: expected_blocksize_of_the_device
            path: expected_unix_device_node

        credentials:
          -
            username: user
            shadow_hash: "password-hash-sha-512-preferred"
            ssh-key:  "public-ssh-key"
          -
            username: rpc
            id: 495
            group: nogroup
            home_dir: /var/lib/empty

        packages:
          directory: path_to_a_package_repository

        call: program_call_directive

    :param str config_file: file path name
    """
    def __init__(self, config_file):
        self.config_data = None

        if os.path.exists(config_file):
            with open(config_file, 'r') as config:
                self.config_data = yaml.load(config)

    def get_config_file_version(self):
        if self.config_data and 'version' in self.config_data:
            return self.config_data['version']

    def get_instance_type(self):
        if self.config_data and 'instance_type' in self.config_data:
            if self.config_data['instance_type'] == 'VeryLargeInstance':
                return InstanceType.vli
            else:
                return InstanceType.li

    def get_network_config(self):
        if self.config_data and 'blade' in self.config_data:
            if 'networking' in self.config_data['blade']:
                return self.config_data['blade']['networking']

    def get_user_config(self):
        if 'credentials' in self.config_data:
            return self.config_data['credentials']

    def get_call_script(self):
        if 'call' in self.config_data:
            return self.config_data['call']
