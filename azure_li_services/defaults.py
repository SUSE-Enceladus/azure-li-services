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

from azure_li_services.exceptions import AzureLiConfigFileNotFoundException


class Defaults(object):
    """
    **Implements default values**

    Provides class methods for default values
    """
    @classmethod
    def get_config_file_name(self):
        return '/etc/suse_firstboot_config.yaml'

    @classmethod
    def get_config_file(self):
        """
        Provides config file as stored locally

        Given the config_lookup service has found and imported
        the Azure LI/VLI config file, this method returns its
        location. If there is no such file an exception is
        raised
        """
        config_file = Defaults.get_config_file_name()
        if os.path.exists(config_file):
            return config_file
        else:
            raise AzureLiConfigFileNotFoundException(
                'No Azure Li/VLi file found: {0}'.format(config_file)
            )
