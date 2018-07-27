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

# project
from azure_li_services.defaults import Defaults


def main():
    """
    Azure Li/Vli status report

    Report overall service status in an update to /etc/issue
    if not all services were successful
    """
    service_reports = Defaults.get_service_reports()

    failed_services = []
    for report in service_reports:
        success = report.get_state()
        if not success:
            failed_services.append(report.get_systemd_service())

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
