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
import glob

# project
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.command import Command
from azure_li_services.path import Path
from azure_li_services.status_report import StatusReport


def main():
    """
    Azure Li/Vli package installation

    Creates a local rpm-md repository and registers it with zypper.
    Installs all packages configured in the scope of an Azure
    Li/Vli instance
    """
    status = StatusReport('install')
    config = RuntimeConfig(Defaults.get_config_file())
    packages_config = config.get_packages_config()

    if packages_config:
        install_source = Defaults.mount_config_source()

        try:
            local_repos = {}
            local_repos.update(
                import_raw_sources(packages_config, install_source)
            )
            local_repos.update(
                import_repository_sources(packages_config, install_source)
            )
            for repository_name, repository_metadata in local_repos.items():
                repository_location = repository_metadata[0]
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

            packages_to_install = []
            for repository_metadata in local_repos.values():
                packages_to_install.append(repository_metadata[1])
            if packages_to_install:
                Command.run(
                    [
                        'zypper', '--non-interactive',
                        'install', '--auto-agree-with-licenses',
                        ' '.join(filter(None, packages_to_install))
                    ]
                )

        finally:
            Defaults.umount_config_source(install_source)

    status.set_success()


def import_raw_sources(packages_config, source_provider):
    raw_sources = packages_config.get('raw')
    import_data = {}
    if raw_sources:
        repository_name = raw_sources['name']
        repository_location = '/var/lib/localrepos/{0}'.format(
            repository_name
        )
        Path.create(repository_location)
        bash_command = ' '.join(
            ['rsync', '-zav'] + list(
                map(
                    lambda dir_name: '{0}/{1}/*'.format(
                        source_provider.location, dir_name
                    ), raw_sources['directory']
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
        import_data[repository_name] = [repository_location]

        install_items = []
        for package in glob.iglob('{0}/*.rpm'.format(repository_location)):
            install_items.append(
                Command.run(
                    ['rpm', '-qp', '--qf', '%{NAME}', package]
                ).output
            )
        import_data[repository_name].append(
            ' '.join(install_items)
        )
    return import_data


def import_repository_sources(packages_config, source_provider):
    repo_sources = packages_config.get('repository') or []
    import_data = {}
    for repository in repo_sources:
        repository_name = repository['name']
        repository_location = '/var/lib/localrepos/{0}'.format(
            repository_name
        )
        Path.create(repository_location)
        sync_source = repository['source']
        if os.path.isdir(sync_source):
            # normalize source path for rsync, make sure a '/'
            # is appended at the end of the directory specification
            # This impacts the behavior of rsync to sync the contents
            # of the directory into the new location but not the
            # directory itself.
            sync_source = os.path.normpath(sync_source)
            sync_source += os.sep
        Command.run(
            ['rsync', '-zav', sync_source, repository_location]
        )
        if repository.get('source_prefix'):
            import_data[repository_name] = [
                ''.join([repository['source_prefix'], repository_location])
            ]
        else:
            import_data[repository_name] = [repository_location]

        install_items = repository.get('install') or []
        import_data[repository_name].append(
            ' '.join(install_items)
        )
    return import_data
