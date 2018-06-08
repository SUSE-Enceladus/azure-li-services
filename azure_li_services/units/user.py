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
from azure_li_services.users import Users
from azure_li_services.status_report import StatusReport

from azure_li_services.exceptions import AzureHostedUserConfigDataException
from azure_li_services.path import Path


def main():
    """
    Azure Li/Vli user setup

    Creates the configured user and its access setup for ssh
    and sudo services in the scope of an Azure Li/Vli instance
    """
    status = StatusReport('user')
    config = RuntimeConfig(Defaults.get_config_file())

    user_config = config.get_user_config()
    for user in user_config:
        create_or_modify_user(user)
        setup_ssh_authorization(user)
        setup_sudo_authorization(user)

    setup_sudo_config()
    status.set_success()


def create_or_modify_user(user):
    if 'username' not in user:
        raise AzureHostedUserConfigDataException(
            'username missing in config {0}'.format(user)
        )
    options = []
    system_users = Users()
    user_exists = system_users.user_exists(user['username'])
    if 'group' in user:
        if not system_users.group_exists(user['group']):
            system_users.group_add(user['group'], [])
        options += [
            '-g', user['group']
        ]
    if 'shadow_hash' in user:
        options += [
            '-p', user['shadow_hash'],
            '-s', '/bin/bash'
        ]
    else:
        options += [
            '-s', '/sbin/nologin'
        ]
    if not user_exists:
        home_dir = user.get('home_dir') or '/home/{0}'.format(user['username'])
        options += [
            '-m', '-d', home_dir
        ]
    if 'id' in user:
        options += [
            '-u', '{0}'.format(user['id'])
        ]
    if user_exists:
        system_users.user_modify(
            user['username'], options
        )
    else:
        system_users.user_add(
            user['username'], options
        )


def setup_ssh_authorization(user):
    if 'ssh-key' in user:
        ssh_auth_dir = '/home/{0}/.ssh/'.format(
            user['username']
        )
        Path.create(ssh_auth_dir)
        os.chmod(ssh_auth_dir, 0o700)
        with open(ssh_auth_dir + 'authorized_keys', 'a') as ssh:
            ssh.write(os.linesep)
            ssh.write(user['ssh-key'])
        os.chmod(ssh_auth_dir + 'authorized_keys', 0o600)


def setup_sudo_authorization(user):
    if 'shadow_hash' in user and user['username'] != 'root':
        system_users = Users()
        if not system_users.group_exists('admin'):
            system_users.group_add('admin', [])
        system_users.user_modify(
            user['username'], ['-a', '-G', 'admin']
        )


def setup_sudo_config():
    sudo_config = '/etc/sudoers'
    system_users = Users()
    if os.path.exists(sudo_config) and system_users.group_exists('admin'):
        with open(sudo_config, 'a') as sudo:
            sudo.write(os.linesep)
            sudo.write('%admin ALL=(ALL) NOPASSWD: ALL')
