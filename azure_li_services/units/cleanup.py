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
from azure_li_services.logger import Logger
from azure_li_services.command import Command
from azure_li_services.defaults import Defaults


def main():
    """
    Azure Li/Vli cleanup

    Uninstall azure-li-services package and its dependencies
    and check for potential reboot request
    """
    Logger.setup()
    service_reports = Defaults.get_service_reports()

    reboot_system = False
    all_services_successful = True
    for report in service_reports:
        if not report.get_state():
            # in case a service has unknown or failed state we will
            # not consider to reboot the machine
            all_services_successful = False
            reboot_system = False
            break
        if report.get_reboot():
            reboot_system = True

    install_source = Defaults.mount_config_source()
    try:
        state_file = os.sep.join(
            [
                install_source.location,
                'workload_success_is_{}'.format(
                    all_services_successful
                ).lower()
            ]
        )
        with open(state_file, 'w'):
            pass
        if not all_services_successful:
            write_service_log(install_source)
    finally:
        Defaults.umount_config_source(install_source)

    Command.run(
        [
            'zypper', '--non-interactive',
            'remove', '--clean-deps', '--force-resolution',
            'azure-li-services'
        ]
    )
    Command.run(
        [
            'systemctl', 'reset-failed'
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


def write_service_log(install_source):
    log_file = os.sep.join(
        [install_source.location, 'workload.log']
    )
    bash_command = ' '.join(
        ['systemctl', 'status', '-l', '--all', '&>', log_file]
    )
    Command.run(
        ['bash', '-c', bash_command], raise_on_error=False
    )
    Command.run(
        ['cp', Defaults.get_log_file(), install_source.location],
        raise_on_error=False
    )
