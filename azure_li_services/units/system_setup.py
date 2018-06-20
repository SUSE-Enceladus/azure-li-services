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
# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.command import Command
from azure_li_services.status_report import StatusReport


def main():
    """
    Azure Li/Vli system setup

    Runs machine setup tasks in the scope of an Azure Li/Vli instance
    """
    status = StatusReport('system_setup')
    config = RuntimeConfig(Defaults.get_config_file())
    hostname = config.get_hostname()

    if hostname:
        set_hostname(hostname)

    status.set_success()


def set_hostname(hostname):
    Command.run(
        ['hostnamectl', 'set-hostname', hostname]
    )
