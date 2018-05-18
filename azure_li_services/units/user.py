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

from azure_li_services.exceptions import AzureHostedUserConfigDataException
from azure_li_services.path import Path


def main():
    """
    Azure Li/Vli user setup

    Creates the configured user and its access setup for ssh
    and sudo services in the scope of an Azure Li/Vli instance
    """
    config = RuntimeConfig(Defaults.get_config_file())
    user_config = config.get_user_config()

    create_user(user_config)
    setup_ssh_authorization(user_config)
    setup_sudo_authorization(user_config)


def create_user(user_config):
    if 'username' not in user_config or 'shadow_hash' not in user_config:
        raise AzureHostedUserConfigDataException(
            'At least one of {0} missing in {1}'.format(
                ('username', 'shadow_hash'), user_config
            )
        )
    options = [
        '-p', user_config['shadow_hash'],
        '-s', '/bin/bash',
        '-m', '-d', '/home/{0}'.format(user_config['username'])
    ]
    Command.run(
        ['useradd'] + options + [user_config['username']]
    )


def setup_ssh_authorization(user_config):
    if 'ssh-key' in user_config:
        ssh_auth_dir = '/home/{0}/.ssh/'.format(
            user_config['username']
        )
        Path.create(ssh_auth_dir)
        with open(ssh_auth_dir + 'authorized_keys', 'a') as ssh:
            ssh.write(os.linesep)
            ssh.write(user_config['ssh-key'])


def setup_sudo_authorization(user_config):
    sudo_config = '/etc/sudoers'
    if os.path.exists(sudo_config):
        Command.run(
            ['groupadd', 'admin']
        )
        Command.run(
            ['usermod', '-a', '-G', 'admin', user_config['username']]
        )
        with open(sudo_config, 'a') as sudo:
            sudo.write(os.linesep)
            sudo.write('%admin ALL=(ALL) NOPASSWD: ALL')
