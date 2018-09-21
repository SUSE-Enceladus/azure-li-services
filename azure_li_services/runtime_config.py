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
from cerberus import Validator

# project
from azure_li_services.schema import schema
from azure_li_services.instance_type import InstanceType

from azure_li_services.exceptions import AzureHostedConfigDataException


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
        instance_type: LargeInstance|VeryLargeInstance
        sku: identifier_string
        hostname: name_string

        machine_constraints:
          min_cores: number_of_cores
          min_memory: main_memory_value_with_unit

        networking:
          -
            interface: eth0
            vlan: vlan_number
            ip: 10.250.10.51
            gateway: 10.250.10.1
            subnet_mask: 255.255.255.0

        storage:
          -
            file_system: nfs
            min_size:  storage_size_value_with_unit
            device: "10.250.21.12:/nfs/share"
            mount: "/mnt/foo"
            mount_options:
              - a
              - b
              - c

        credentials:
          -
            username: user
            shadow_hash: "password-hash-sha-512-preferred"
            ssh-key:  "public-ssh-key"
          -
            username: rpc
            id: 495
            group:
              name: nogroup
            home_dir: /var/lib/empty

        packages:
          directory: path_to_a_package_repository

        call: path/to/executable/file

    :param str config_file: file path name
    """
    def __init__(self, config_file):
        self.config_data = None

        if os.path.exists(config_file):
            with open(config_file, 'r') as config:
                try:
                    self.config_data = yaml.load(config)
                except Exception as e:
                    raise AzureHostedConfigDataException(
                        'Loading yaml format raises: {0}: {1}'.format(
                            type(e).__name__, e
                        )
                    )
            validator = Validator(schema)
            validator.validate(self.config_data, schema)
            if validator.errors:
                raise AzureHostedConfigDataException(
                    'Config file validation failed with: {0}'.format(
                        validator.errors
                    )
                )

    def get_config_file_version(self):
        if self.config_data:
            return self.config_data.get('version')

    def get_instance_type(self):
        if self.config_data:
            if self.config_data.get('instance_type') == 'VeryLargeInstance':
                return InstanceType.vli
            else:
                return InstanceType.li

    def get_hostname(self):
        if self.config_data:
            return self.config_data.get('hostname')

    def get_crash_dump_config(self):
        if self.config_data:
            return self.config_data.get('crash_dump')

    def get_network_config(self):
        if self.config_data:
            return self.config_data.get('networking')

    def get_machine_constraints(self):
        if self.config_data:
            return self.config_data.get('machine_constraints')

    def get_user_config(self):
        if self.config_data:
            return self.config_data.get('credentials')

    def get_packages_config(self):
        if self.config_data:
            return self.config_data.get('packages')

    def get_call_script(self):
        if self.config_data:
            return self.config_data.get('call')

    def get_storage_config(self):
        if self.config_data:
            return self.config_data.get('storage')
