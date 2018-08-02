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
from collections import OrderedDict

from azure_li_services.command import Command

from azure_li_services.exceptions import (
    AzureHostedConfigFileNotFoundException,
    AzureHostedConfigFileSourceMountException
)


class Defaults(object):
    """
    **Implements default values**

    Provides class methods for default values
    """
    @classmethod
    def get_config_file_name(self):
        return '/etc/suse_firstboot_config.yaml'

    @classmethod
    def get_status_report_directory(self):
        return '/var/lib/azure_li_services'

    @classmethod
    def get_service_reports(self):
        from azure_li_services.status_report import StatusReport
        service_reports = []
        unit_to_service_map = {
            'config_lookup':
                'azure-li-config-lookup',
            'user':
                'azure-li-user',
            'install':
                'azure-li-install',
            'network':
                'azure-li-network',
            'call':
                'azure-li-call',
            'machine_constraints':
                'azure-li-machine-constraints',
            'system_setup':
                'azure-li-system-setup',
            'storage':
                'azure-li-storage'
        }
        unit_to_service_map_ordered = OrderedDict(
            sorted(unit_to_service_map.items())
        )
        for unit, service in unit_to_service_map_ordered.items():
            report = StatusReport(
                unit, init_state=False, systemd_service_name=service
            )
            report.load()
            service_reports.append(report)
        return service_reports

    @classmethod
    def get_config_file(self):
        """
        Provides config file as stored locally

        Given the config_lookup service has found and imported
        the Azure LI/VLI config file, this method returns its
        location. If there is no such file an exception is
        raised
        """
        config_file = Defaults.get_config_file_name()
        if os.path.exists(config_file):
            return config_file
        else:
            raise AzureHostedConfigFileNotFoundException(
                'No Azure Li/VLi file found: {0}'.format(config_file)
            )

    @classmethod
    def mount_config_source(self):
        config_type = namedtuple(
            'config_type', ['name', 'location', 'label']
        )
        azure_config = config_type(
            name=os.path.basename(Defaults.get_config_file_name()),
            location='/mnt', label='azconfig'
        )
        lun_result = Command.run(
            ['mount', '--label', azure_config.label, azure_config.location],
            raise_on_error=False
        )
        if lun_result.returncode != 0:
            iso_result = Command.run(
                ['mount', '/dev/dvd', azure_config.location],
                raise_on_error=False
            )
            if iso_result.returncode != 0:
                raise AzureHostedConfigFileSourceMountException(
                    'Source mount failed with: primary:{0}, fallback{1}'.format(
                        lun_result.error, iso_result.error
                    )
                )

        return azure_config
