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
from azure_li_services.command import Command
from azure_li_services.defaults import Defaults


def main():
    """
    Azure Li/Vli cleanup

    Uninstall azure-li-services package and its dependencies
    and check for potential reboot request
    """
    service_reports = Defaults.get_service_reports()

    reboot_system = False
    for report in service_reports:
        if not report.get_state():
            # in case a service has unknown or failed state we will
            # not consider to reboot the machine
            reboot_system = False
            break
        if report.get_reboot():
            reboot_system = True

    Command.run(
        [
            'zypper', '--non-interactive',
            'remove', '--clean-deps', '--force-resolution',
            'azure-li-services'
        ]
    )

    if reboot_system:
        Command.run(
            [
                'kexec',
                '--load', '/boot/vmlinuz',
                '--initrd', '/boot/initrd',
                '--command-line', get_boot_cmdline()
            ]
        )
        Command.run(
            ['kexec', '--exec']
        )


def get_boot_cmdline():
    effective_boot_options = []
    with open('/proc/cmdline') as cmdline_handle:
        boot_cmdline = cmdline_handle.read().split()

    for option in boot_cmdline:
        if 'vmlinuz' not in option:
            effective_boot_options.append(option)

    return ' '.join(effective_boot_options)
