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
from collections import OrderedDict

# project
from azure_li_services.status_report import StatusReport


def main():
    """
    Azure Li/Vli status report

    Report overall service status in an update to /etc/issue
    if not all services were successful
    """
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
    failed_services = []
    for unit, service in unit_to_service_map_ordered.items():
        report = StatusReport(unit, init_state=False)
        report.load()
        success = report.get_state()
        if not success:
            failed_services.append(service)

    if failed_services:
        report_services_failed(failed_services)


def report_services_failed(failed_services):
    with open('/etc/issue', 'w') as issue:
        issue.write(os.linesep)
        issue.write('!!! DEPLOYMENT ERROR !!!')
        issue.write(os.linesep)
        issue.write(
            'For details see: "systemctl status -l {0}"'.format(
                ' '.join(failed_services)
            )
        )
        issue.write(os.linesep)
        issue.write(os.linesep)
