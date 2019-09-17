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
import select
import os
import subprocess
from collections import namedtuple
import logging

# project
from .exceptions import (
    AzureHostedCommandException,
    AzureHostedCommandNotFoundException
)

logger = logging.getLogger('Azure_LI_Services')


class Command(object):
    """
    **Implements command invocation**

    An instance of Command provides methods to invoke external
    commands in blocking and non blocking mode. Control of
    stdout and stderr is given to the caller
    """
    @classmethod
    def run(self, command, custom_env=None, raise_on_error=True):
        """
        Execute a program and block the caller. The return value
        is a hash containing the stdout, stderr and return code
        information. Unless raise_on_error is set to false an
        exception is thrown if the command exits with an error
        code not equal to zero

        Example:

        .. code:: python

            result = Command.run(['ls', '-l'])

        :param list command: command and arguments
        :param list custom_env: custom os.environ
        :param bool raise_on_error: control error behaviour

        :return:
            Contains call results in command type

            .. code:: python

                command(output='string', error='string', returncode=int)

        :rtype: namedtuple
        """
        from .path import Path
        command_type = namedtuple(
            'command', ['output', 'error', 'returncode']
        )
        environment = os.environ
        if custom_env:
            environment = custom_env
        if not Path.which(
            command[0], custom_env=environment, access_mode=os.X_OK
        ):
            message = 'Command "%s" not found in the environment' % command[0]
            if not raise_on_error:
                return command_type(
                    output=None,
                    error=None,
                    returncode=-1
                )
            else:
                raise AzureHostedCommandNotFoundException(message)
        try:
            logger.info('Calling: {0}'.format(command))
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment
            )
        except Exception as e:
            raise AzureHostedCommandException(
                '%s: %s: %s' % (command[0], type(e).__name__, format(e))
            )
        output, error = process.communicate()
        if process.returncode != 0 and not error:
            error = bytes(b'(no output on stderr)')
        if process.returncode != 0 and not output:
            output = bytes(b'(no output on stdout)')
        if process.returncode != 0 and raise_on_error:
            raise AzureHostedCommandException(
                '%s: stderr: %s, stdout: %s' % (
                    command[0], error.decode(), output.decode()
                )
            )
        return command_type(
            output=output.decode(),
            error=error.decode(),
            returncode=process.returncode
        )

    @classmethod
    def call(self, command, custom_env=None):
        """
        Execute a program and return an io file handle pair back.
        stdout and stderr are both on different channels. The caller
        must read from the output file handles in order to actually
        run the command. This can be done using the CommandIterator
        from command_process

        Example:

        .. code:: python

            process = Command.call(['ls', '-l'])

        :param list command: command and arguments
        :param list custom_env: custom os.environ

        :return:
            Contains process results in command type

            .. code:: python

                command(
                    output='string', output_available=bool,
                    error='string', error_available=bool,
                    process=subprocess
                )

        :rtype: namedtuple
        """
        from .path import Path
        environment = os.environ
        if custom_env:
            environment = custom_env
        if not Path.which(
            command[0], custom_env=environment, access_mode=os.X_OK
        ):
            raise AzureHostedCommandNotFoundException(
                'Command "%s" not found in the environment' % command[0]
            )
        try:
            logger.info('Calling: {0}'.format(command))
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment
            )
        except Exception as e:
            raise AzureHostedCommandException(
                '%s: %s' % (type(e).__name__, format(e))
            )

        def output_available():
            def _select():
                descriptor_lists = select.select(
                    [process.stdout], [], [process.stdout], 1e-4
                )
                readable = descriptor_lists[0]
                exceptional = descriptor_lists[2]
                if readable and not exceptional:
                    return True
            return _select

        def error_available():
            def _select():
                descriptor_lists = select.select(
                    [process.stderr], [], [process.stderr], 1e-4
                )
                readable = descriptor_lists[0]
                exceptional = descriptor_lists[2]
                if readable and not exceptional:
                    return True
            return _select

        command = namedtuple(
            'command', [
                'output', 'output_available',
                'error', 'error_available',
                'process'
            ]
        )
        return command(
            output=process.stdout,
            output_available=output_available(),
            error=process.stderr,
            error_available=error_available(),
            process=process
        )
