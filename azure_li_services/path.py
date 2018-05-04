# Copyright (c) 2017 SUSE Linux GmbH.  All rights reserved.
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
from .command import Command


class Path(object):
    """
    **Directory path helpers**
    """
    @classmethod
    def create(self, path):
        """
        Create path and all sub directories to target

        :param string path: path name
        """
        Command.run(
            ['mkdir', '-p', path]
        )

    @classmethod
    def wipe(self, path):
        """
        Delete path and all contents

        :param string path: path name
        """
        Command.run(
            ['rm', '-r', '-f', path]
        )

    @classmethod
    def remove(self, path):
        """
        Delete empty path, causes an error if target is not empty

        :param string path: path name
        """
        Command.run(
            ['rmdir', path]
        )

    @classmethod
    def which(
        self, filename, alternative_lookup_paths=None,
        custom_env=None, access_mode=None
    ):
        """
        Lookup file name in PATH

        :param string filename: file base name
        :param list alternative_lookup_paths: list of additional lookup paths
        :param list custom_env: a custom os.environ
        :param int access_mode: one of the os access modes or a combination of
         them (os.R_OK, os.W_OK and os.X_OK). If the provided access mode
         does not match the file is considered not existing

        :return: absolute path to file or None

        :rtype: str
        """
        lookup_paths = []
        multipart_message = [
            '"%s": ' % filename, 'exists: unknown', 'mode match: not checked'
        ]
        system_path = os.environ.get('PATH')
        if custom_env:
            system_path = custom_env.get('PATH')
        if system_path:
            lookup_paths = system_path.split(os.pathsep)
        if alternative_lookup_paths:
            lookup_paths += alternative_lookup_paths
        multipart_message[0] += 'in paths "%s"' % ':'.join(lookup_paths)
        for path in lookup_paths:
            location = os.path.join(path, filename)
            file_exists = os.path.exists(location)
            multipart_message[1] = 'exists: "%s"' % file_exists
            if access_mode and file_exists:
                mode_match = os.access(location, access_mode)
                multipart_message[2] = 'mode match: "%s"' % mode_match
                if mode_match:
                    return location
            elif file_exists:
                return location
