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
import pwd
import grp

# project
from azure_li_services.logger import Logger
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.defaults import Defaults
from azure_li_services.users import Users
from azure_li_services.status_report import StatusReport

from azure_li_services.path import Path
from azure_li_services.command import Command

from azure_li_services.exceptions import (
    AzureHostedException,
    AzureHostedUserConfigDataException
)


def main():
    """
    Azure Li/Vli user setup

    Creates the configured user and its access setup for ssh
    and sudo services in the scope of an Azure Li/Vli instance
    """
    Logger.setup()
    status = StatusReport('user')
    config = RuntimeConfig(Defaults.get_config_file())

    user_config = config.get_user_config()

    if not user_config:
        raise AzureHostedUserConfigDataException(
            'credentials section missing in config file'
        )

    user_setup_errors = []

    for user in user_config:
        try:
            create_or_modify_user(user)
        except Exception as issue:
            user_setup_errors.append(issue)
        else:
            try:
                setup_ssh_authorization(user)
            except Exception as issue:
                user_setup_errors.append(issue)
            try:
                setup_sudo_authorization(user)
            except Exception as issue:
                user_setup_errors.append(issue)
            try:
                setup_user_attributes(user)
            except Exception as issue:
                user_setup_errors.append(issue)

    setup_sudo_config()

    if user_setup_errors:
        raise AzureHostedException(user_setup_errors)

    status.set_success()


def create_or_modify_user(user):
    if 'username' not in user:
        raise AzureHostedUserConfigDataException(
            'username missing in config {0}'.format(user)
        )
    user_options = []
    system_users = Users()
    user_exists = system_users.user_exists(user['username'])
    if 'group' in user:
        group_setup = user['group']
        if not system_users.group_exists(group_setup['name']):
            group_options = []
            if 'id' in group_setup:
                group_options += [
                    '-g', '{0}'.format(group_setup['id'])
                ]
            system_users.group_add(group_setup['name'], group_options)

        user_options += [
            '-g', group_setup['name']
        ]
    if 'shadow_hash' in user:
        user_options += [
            '-p', user['shadow_hash'],
            '-s', '/bin/bash'
        ]
    elif 'ssh-key' in user:
        user_options += [
            '-s', '/bin/bash'
        ]
    else:
        user_options += [
            '-s', '/sbin/nologin'
        ]
    if not user_exists:
        home_dir = user.get('home_dir') or '/home/{0}'.format(user['username'])
        user_options += [
            '-m', '-d', home_dir
        ]
    if 'id' in user:
        user_options += [
            '-u', '{0}'.format(user['id'])
        ]
    if user_exists:
        system_users.user_modify(
            user['username'], user_options
        )
    else:
        system_users.user_add(
            user['username'], user_options
        )


def setup_ssh_authorization(user):
    if 'ssh-key' in user or 'ssh-private-key' in user:
        if user['username'] == 'root':
            ssh_auth_dir = '/root/.ssh/'
            default_group = 'root'
        else:
            ssh_auth_dir = '/home/{0}/.ssh/'.format(
                user['username']
            )
            default_group = 'users'
        Path.create(ssh_auth_dir)
        group_setup = user['group'] if 'group' in user else {}
        uid = pwd.getpwnam(user['username']).pw_uid
        gid = grp.getgrnam(group_setup.get('name') or default_group).gr_gid
        os.chmod(ssh_auth_dir, 0o700)
        if user['username'] != 'root':
            os.chown(ssh_auth_dir, uid, gid)
        if 'ssh-key' in user:
            ssh_auth_file = ssh_auth_dir + 'authorized_keys'
            with open(ssh_auth_file, 'a') as ssh:
                ssh.write(os.linesep)
                ssh.write(user['ssh-key'])
            os.chmod(ssh_auth_file, 0o600)
            if user['username'] != 'root':
                os.chown(ssh_auth_file, uid, gid)
        if 'ssh-private-key' in user:
            ssh_key_source = Defaults.mount_config_source()
            private_key_file = user['ssh-private-key']
            Command.run(
                [
                    'cp', os.sep.join(
                        [ssh_key_source.location, private_key_file]
                    ), ssh_auth_dir
                ]
            )
            ssh_key_file = os.path.normpath(
                os.sep.join(
                    [ssh_auth_dir, os.path.basename(private_key_file)]
                )
            )
            os.chmod(ssh_key_file, 0o600)
            if user['username'] != 'root':
                os.chown(ssh_key_file, uid, gid)


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


def setup_user_attributes(user):
    if user.get('require_password_change'):
        system_users = Users()
        system_users.setup_change_password_on_logon(
            user['username']
        )
