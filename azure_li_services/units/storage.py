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
import humanfriendly
import shutil

# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.command import Command
from azure_li_services.status_report import StatusReport
from azure_li_services.path import Path

from azure_li_services.exceptions import AzureHostedStorageMountException


def main():
    """
    Azure Li/Vli storage mount setup

    Updates fstab with new storage mount entries and activates
    them in the scope of an Azure Li/Vli instance
    """
    status = StatusReport('storage')
    config = RuntimeConfig(Defaults.get_config_file())
    storage_config = config.get_storage_config()

    if storage_config:
        fstab_entries = []
        for storage in storage_config:
            if 'device' not in storage or 'mount' not in storage:
                raise AzureHostedStorageMountException(
                    'At least one of {0} missing in {1}'.format(
                        ('device', 'mount'), storage
                    )
                )
            Path.create(storage['mount'])
            fstab_entries.append(
                '{device} {mount} {fstype} {options} 0 0'.format(
                    device=storage['device'],
                    mount=storage['mount'],
                    fstype=storage.get('file_system') or 'auto',
                    options=','.join(
                        storage.get('mount_options', ['defaults'])
                    )
                )
            )

        if fstab_entries:
            with open('/etc/fstab', 'a') as fstab:
                fstab.write(os.linesep)
                for entry in fstab_entries:
                    fstab.write(entry)
                    fstab.write(os.linesep)

            Command.run(['mount', '-a'])

            for storage in storage_config:
                min_size = storage.get('min_size')
                if min_size:
                    check_storage_size_validates_constraint(
                        min_size, storage['mount']
                    )

            status.set_success()


def check_storage_size_validates_constraint(min_size, mount_point):
    min_bytes = humanfriendly.parse_size(min_size, binary=True)
    disk_usage = shutil.disk_usage(mount_point)
    if disk_usage.free < min_bytes:
        raise AzureHostedStorageMountException(
            'Free space: {0}={1} is below required minimum: {2}'.format(
                mount_point,
                humanfriendly.format_size(disk_usage.free, binary=True),
                humanfriendly.format_size(min_bytes, binary=True)
            )
        )
