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
from collections import namedtuple

# project
from azure_li_services.command import Command
from azure_li_services.path import Path
from azure_li_services.exceptions import AzureHostedConfigFileNotFoundException
from azure_li_services.defaults import Defaults


def main():
    """
    Azure Li/Vli config file lookup

    Lookup config file as provided by the Azure Li/VLi storage backend
    and make it locally available at the location described by
    Defaults.get_config_file_name()
    """
    config_type = namedtuple(
        'config_type', ['name', 'location', 'label']
    )
    azure_config = config_type(
        name=os.path.basename(Defaults.get_config_file_name()),
        location='/mnt', label='azconfig'
    )

    Command.run(
        ['mount', '--label', azure_config.label, azure_config.location]
    )

    try:
        azure_config_lookup_paths = [azure_config.location]
        azure_config_file = Path.which(
            azure_config.name, azure_config_lookup_paths
        )
        if not azure_config_file:
            raise AzureHostedConfigFileNotFoundException(
                'Config file not found at: {0}/{1}'.format(
                    azure_config.location, azure_config.name
                )
            )
        Path.create(
            os.path.dirname(Defaults.get_config_file_name())
        )
        Command.run(
            ['cp', azure_config_file, Defaults.get_config_file_name()]
        )
        os.chmod(Defaults.get_config_file_name(), 0o600)
    finally:
        Command.run(['umount', azure_config.location])
