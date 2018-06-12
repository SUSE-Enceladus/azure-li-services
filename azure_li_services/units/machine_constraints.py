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
import multiprocessing
import humanfriendly
from psutil import virtual_memory

# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.status_report import StatusReport

from azure_li_services.exceptions import AzureHostedMachineConstraintException


def main():
    """
    Azure Li/Vli machine constraints

    Validation of machine requirements in the scope of an Azure Li/Vli instance
    """
    status = StatusReport('machine_constraints')
    config = RuntimeConfig(Defaults.get_config_file())
    machine_constraints = config.get_machine_constraints()

    if machine_constraints:
        check_cpu_count_validates_constraint(
            machine_constraints
        )
        check_main_memory_validates_constraint(
            machine_constraints
        )

    status.set_success()


def check_cpu_count_validates_constraint(machine_constraints):
    min_cores = machine_constraints.get('min_cores')
    if min_cores:
        existing_cores = multiprocessing.cpu_count()
        if existing_cores < int(min_cores):
            raise AzureHostedMachineConstraintException(
                'Number of cores: {0} is below required minimum: {1}'.format(
                    existing_cores, min_cores
                )
            )


def check_main_memory_validates_constraint(machine_constraints):
    min_memory = machine_constraints.get('min_memory')
    if min_memory:
        min_bytes = humanfriendly.parse_size(min_memory, binary=True)
        existing_memory = virtual_memory()
        if existing_memory.total < min_bytes:
            raise AzureHostedMachineConstraintException(
                'Main memory: {0} is below required minimum: {1}'.format(
                    humanfriendly.format_size(
                        existing_memory.total, binary=True
                    ),
                    humanfriendly.format_size(
                        min_bytes, binary=True
                    )
                )
            )
