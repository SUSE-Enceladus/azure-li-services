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
from azure_li_services.path import Path
from azure_li_services.defaults import Defaults


class StatusReport(object):
    """
    **Implements status report interface**

    Creating an instance of StatusReport will initialize the
    provided service name with a default failed state. It's
    in the responsibility of the service implementation to
    set the success state when appropriate.

    :param str service_name: name of the service
    """
    def __init__(
        self, service_name, init_state=True, systemd_service_name=None
    ):
        self.systemd_service_name = systemd_service_name
        self.status = {
            service_name: {
                'success': None,
                'reboot': False
            }
        }
        self.service_name = service_name
        self.status_directory = Defaults.get_status_report_directory()
        self.status_file = os.sep.join(
            [self.status_directory, self.service_name + '.report.yaml']
        )
        if not os.path.exists(self.status_directory):
            Path.create(self.status_directory)

        if init_state:
            self.set_failed()

    def set_success(self):
        self.status[self.service_name]['success'] = True
        self._write()

    def set_failed(self):
        self.status[self.service_name]['success'] = False
        self._write()

    def set_reboot_required(self):
        self.status[self.service_name]['reboot'] = True
        self._write()

    def load(self):
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as report:
                self.status = yaml.safe_load(report)

    def get_state(self):
        return self.status[self.service_name]['success']

    def get_reboot(self):
        return self.status[self.service_name]['reboot']

    def get_systemd_service(self):
        return self.systemd_service_name

    def _write(self):
        with open(self.status_file, 'w') as report:
            yaml.dump(self.status, report, default_flow_style=False)
