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
import hashlib
import re
from psutil import virtual_memory

# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.instance_type import InstanceType
from azure_li_services.defaults import Defaults
from azure_li_services.command import Command
from azure_li_services.status_report import StatusReport

from azure_li_services.exceptions import (
    AzureHostedException,
    AzureHostedCommandOutputException
)


def main():
    """
    Azure Li/Vli system setup

    Runs machine setup tasks in the scope of an Azure Li/Vli instance
    """
    status = StatusReport('system_setup')
    config = RuntimeConfig(Defaults.get_config_file())
    hostname = config.get_hostname()
    instance_type = config.get_instance_type()
    stonith_config = config.get_stonith_config()

    system_setup_errors = []

    if hostname:
        try:
            set_hostname(hostname)
        except Exception as issue:
            system_setup_errors.append(issue)

    if stonith_config:
        try:
            set_stonith_service(stonith_config)
            enable_extra_kernel_modules()
        except Exception as issue:
            system_setup_errors.append(issue)

    try:
        set_kdump_service(
            config.get_crash_dump_config(), status
        )
    except Exception as issue:
        system_setup_errors.append(issue)

    try:
        set_kernel_samepage_merging_mode()
    except Exception as issue:
        system_setup_errors.append(issue)

    try:
        set_energy_performance_settings()
    except Exception as issue:
        system_setup_errors.append(issue)

    try:
        set_saptune_service()
    except Exception as issue:
        system_setup_errors.append(issue)

    if instance_type == InstanceType.vli:
        try:
            set_reboot_intervention()
        except Exception as issue:
            system_setup_errors.append(issue)

    if system_setup_errors:
        raise AzureHostedException(system_setup_errors)

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
        ['systemctl', 'enable', 'tuned']
    )
    Command.run(
        ['systemctl', 'start', 'tuned']
    )
    Command.run(
        ['saptune', 'daemon', 'start']
    )
    Command.run(
        ['saptune', 'solution', 'apply', 'HANA']
    )
    if os.path.exists('/usr/lib/tuned/sap-hana'):
        Command.run(
            ['tuned-adm', 'profile', 'sap-hana']
        )
    else:
        Command.run(
            ['tuned-adm', 'profile', 'sapconf']
        )


def set_reboot_intervention():
    efi_boot_dir = '/boot/efi/'
    if os.path.exists(efi_boot_dir):
        with open(efi_boot_dir + 'startup.nsh', 'w') as efi_startup:
            efi_startup.write(
                'fs0:\efi\sles_sap\grubx64.efi{0}'.format(os.linesep)
            )


def set_kdump_service(config, status):
    if config and config.get('activate') is False:
        # activation of kernel crash dump setup is unwanted
        return

    calibrated = _kdump_calibrate(
        config.get('crash_kernel_high') if config else None,
        config.get('crash_kernel_low') if config else None
    )
    grub_defaults_file = '/etc/default/grub'
    grub_defaults_data = None
    grub_defaults_digest = hashlib.sha256()
    with open(grub_defaults_file, 'r') as grub_defaults_handle:
        grub_defaults_data = grub_defaults_handle.read()

    grub_defaults_digest.update(format(grub_defaults_data).encode())
    grub_defaults_shasum_orig = grub_defaults_digest.hexdigest()

    grub_defaults_data = re.sub(
        r'crashkernel=[0-9]+M,low', 'crashkernel={0}M,low'.format(
            calibrated['Low']
        ), grub_defaults_data
    )
    grub_defaults_data = re.sub(
        r'crashkernel=[0-9]+M,high', 'crashkernel={0}M,high'.format(
            calibrated['High']
        ), grub_defaults_data
    )

    grub_defaults_digest.update(format(grub_defaults_data).encode())
    grub_defaults_shasum_new = grub_defaults_digest.hexdigest()

    if grub_defaults_shasum_orig != grub_defaults_shasum_new:
        with open(grub_defaults_file, 'w') as grub_defaults_handle:
            grub_defaults_handle.write(grub_defaults_data)
        status.set_reboot_required()

    Command.run(
        ['grub2-mkconfig', '-o', '/boot/grub2/grub.cfg']
    )
    Command.run(
        ['systemctl', 'restart', 'kdump']
    )


def set_stonith_service(config):
    # 1. setup InitiatorName
    initiator_name = 'iqn.1996-04.de.suse:01:{0}'.format(
        config['initiatorname']
    )
    initiator_file = '/etc/iscsi/initiatorname.iscsi'
    initiator_data = re.sub(
        r'InitiatorName=.*', 'InitiatorName={0}'.format(initiator_name),
        _read_file(initiator_file)
    )
    _write_file(initiator_file, initiator_data)

    # 2. setup iscsi options
    iscsi_conf = '/etc/iscsi/iscsid.conf'
    iscsi_conf_data = _read_file(iscsi_conf)
    iscsi_conf_data = re.sub(
        r'node.session.timeo.replacement_timeout = .*',
        'node.session.timeo.replacement_timeout = 5',
        iscsi_conf_data
    )
    iscsi_conf_data = re.sub(
        r'node.startup = .*', 'node.startup = automatic',
        iscsi_conf_data
    )
    _write_file(iscsi_conf, iscsi_conf_data)

    # 3. initialize iSCSI devices
    discovery_output = Command.run(
        [
            'iscsiadm', '-m', 'discovery',
            '-t', 'st', '-p', '{0}:3260'.format(config['ip'])
        ]
    ).output.splitlines()

    # 4. create sbd device
    # The first line of the iscsiadm discovery output is taken into
    # account as we expect any group tag to respond with the same
    # target name. We also expect the discovery output to be in the
    # format: target_IP:port,target_portal_group_tag proper_target_name
    discovery_format = '.*:.*,.* .*'
    if discovery_output and re.match(discovery_format, discovery_output[0]):
        target_name = discovery_output[0].split(' ')[1]
        target_device = '/dev/disk/by-path/ip-{0}:3260-iscsi-{1}-lun-0'.format(
            config['ip'], target_name
        )
        Command.run(
            ['iscsiadm', '-m', 'node', '-l']
        )
        Command.run(
            ['rescan-scsi-bus.sh']
        )
        Command.run(
            ['sbd', '-d', target_device, 'create']
        )
        Command.run(
            ['sbd', '-d', target_device, 'dump']
        )
        _write_file(
            '/etc/sysconfig/sbd', 'SBD_DEVICE="{0}"'.format(target_device)
        )
    else:
        raise AzureHostedCommandOutputException(
            'Stonith: Unexpected iSCSI discovery information: {0}'.format(
                discovery_output
            )
        )


def enable_extra_kernel_modules():
    modules = Defaults.get_stonith_needed_modules()
    file_content = ''
    for module in modules:
        file_content = ''.join([file_content, os.linesep, module])
        Command.run(
            ['modprobe', module]
        )

    load_module_path = Defaults.get_extra_kernel_modules_file_name()
    _write_file(load_module_path, file_content)


def _read_file(filename):
    with open(filename, 'r') as file_handle:
        return file_handle.read()


def _write_file(filename, data):
    with open(filename, 'w') as file_handle:
        file_handle.write(data)


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

        # update High value on machines with more than 1TB of main memory
        machine_memory = virtual_memory()
        machine_memory_tbytes = int(machine_memory.total / 1024**4)
        if machine_memory_tbytes > 1:
            calibration_values['High'] *= machine_memory_tbytes
    return calibration_values


def _write_boot_local(entries):
    permanent_boot_setup_file = '/etc/init.d/boot.local'
    with open(permanent_boot_setup_file, 'a') as boot_local:
        for entry in entries:
            boot_local.write(' '.join(entry) + os.linesep)
    os.chmod(permanent_boot_setup_file, 0o755)
