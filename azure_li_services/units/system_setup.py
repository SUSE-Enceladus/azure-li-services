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

    set_kdump_service(
        config.get_crash_kernel_high(), config.get_crash_kernel_low()
    )
    set_kernel_samepage_merging_mode()
    set_energy_performance_settings()
    set_saptune_service()

    status.set_success()


def set_hostname(hostname):
    Command.run(
        ['hostnamectl', 'set-hostname', hostname]
    )


def set_kernel_samepage_merging_mode():
    same_page_mode = '/sys/kernel/mm/ksm/run'
    with open(same_page_mode, 'w') as ksm_run:
        # stop ksmd from running but keep merged pages
        ksm_run.write('0{0}'.format(os.linesep))
    _write_boot_local(
        [['echo', '0', '>', same_page_mode]]
    )


def set_energy_performance_settings():
    cpupower_calls = [
        # set CPU Frequency/Voltage scaling
        ['cpupower', 'frequency-set', '-g', 'performance'],
        # set low latency and maximum performance
        ['cpupower', 'set', '-b', '0']
    ]
    for cpupower_call in cpupower_calls:
        Command.run(cpupower_call)
    _write_boot_local(cpupower_calls)


def set_saptune_service():
    Command.run(
        ['saptune', 'daemon', 'start']
    )
    Command.run(
        ['saptune', 'solution', 'apply', 'HANA']
    )
    Command.run(
        ['tuned-adm', 'profile', 'sap-hana']
    )
    Command.run(
        ['systemctl', 'enable', 'tuned']
    )
    Command.run(
        ['systemctl', 'start', 'tuned']
    )


def set_kdump_service(high, low):
    calibrated = _kdump_calibrate(high, low)
    grub_defaults = '/etc/default/grub'
    Command.run(
        [
            'sed', '-ie',
            's@crashkernel=[0-9]\+M,low@crashkernel={0}M,low@'.format(
                calibrated['Low']
            ),
            grub_defaults
        ]
    )
    Command.run(
        [
            'sed', '-ie',
            's@crashkernel=[0-9]\+M,high@crashkernel={0}M,high@'.format(
                calibrated['High']
            ),
            grub_defaults
        ]
    )
    Command.run(
        ['grub2-mkconfig', '-o', '/boot/grub2/grub.cfg']
    )
    Command.run(
        ['systemctl', 'restart', 'kdump']
    )


def _kdump_calibrate(high, low):
    calibration_values = {
        'Low': low,
        'High': high
    }
    if not high and not low:
        kdumptool_call = Command.run(
            ['kdumptool', 'calibrate']
        )
        for setting in kdumptool_call.output.split(os.linesep):
            try:
                (key, value) = setting.split(':')
            except Exception:
                # ignore setting not in key:value format
                pass
            calibration_values[key] = int(value)
    return calibration_values


def _write_boot_local(entries):
    permanent_boot_setup_file = '/etc/init.d/boot.local'
    with open(permanent_boot_setup_file, 'a') as boot_local:
        for entry in entries:
            boot_local.write(' '.join(entry) + os.linesep)
    os.chmod(permanent_boot_setup_file, 0o755)
