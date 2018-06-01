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
import glob
from collections import namedtuple

# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.command import Command
from azure_li_services.path import Path


def main():
    """
    Azure Li/Vli package installation

    Creates a local rpm-md repository and registers it with zypper.
    Installs all packages configured in the scope of an Azure
    Li/Vli instance
    """
    config = RuntimeConfig(Defaults.get_config_file())
    packages_config = config.get_packages_config()

    source_type = namedtuple(
        'source_type', ['location', 'label']
    )
    call_source = source_type(
        location='/mnt', label='azconfig'
    )

    if 'directory' in packages_config:
        Command.run(
            ['mount', '--label', call_source.label, call_source.location]
        )
        try:
            repository_name = packages_config.get('repository_name') or \
                'azure_{0}'.format(config.get_instance_type())
            repository_location = '/var/lib/localrepos/{0}'.format(
                repository_name
            )
            Path.create(repository_location)
            bash_command = ' '.join(
                ['rsync', '-zav'] + list(
                    map(
                        lambda dir_name: '{0}/{1}/*'.format(
                            call_source.location, dir_name
                        ), packages_config['directory']
                    )
                ) + [
                    repository_location
                ]
            )
            Command.run(
                ['bash', '-c', bash_command]
            )
            Command.run(
                ['createrepo', repository_location]
            )
            Command.run(
                [
                    'zypper', 'removerepo', repository_name
                ], raise_on_error=False
            )
            Command.run(
                [
                    'zypper', 'addrepo', '--no-gpgcheck',
                    repository_location, repository_name
                ]
            )
            install_items = []
            for package in glob.iglob('{0}/*.rpm'.format(repository_location)):
                install_items.append(
                    Command.run(
                        ['rpm', '-qp', '--qf', '%{NAME}', package]
                    ).output
                )
            if install_items:
                Command.run(
                    [
                        'zypper', '--non-interactive',
                        'install', '--auto-agree-with-licenses'
                    ] + install_items
                )
        finally:
            Command.run(['umount', call_source.location])