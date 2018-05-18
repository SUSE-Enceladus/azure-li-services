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
from collections import namedtuple

# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.command import Command


def main():
    """
    Azure Li/Vli script call

    Calls a custom script in the scope of an Azure Li/Vli instance
    """
    config = RuntimeConfig(Defaults.get_config_file())
    call_script = config.get_call_script()

    source_type = namedtuple(
        'source_type', ['location', 'label']
    )
    call_source = source_type(
        location='/mnt', label='azconfig'
    )
    if call_script:
        Command.run(
            ['mount', '--label', call_source.label, call_source.location]
        )
        try:
            Command.run(
                [
                    'bash', '-c', '{0}/{1}'.format(
                        call_source.location, call_script
                    )
                ]
            )
        finally:
            Command.run(['umount', call_source.location])
