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


class AzureHostedException(Exception):
    """
    Base class to handle all known exceptions.

    Specific exceptions are implemented as sub classes of AzureHostedException

    :param string message: Exception message text
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return format(self.message)


class AzureHostedConfigFileNotFoundException(AzureHostedException):
    """
    Exception raised if Azure Li/VLi config file could not
    be found at the expected path on the local system
    """


class AzureHostedConfigDataException(AzureHostedException):
    """
    Exception raised if reading or validating the yaml config file failed
    """


class AzureHostedConfigFileSourceMountException(AzureHostedException):
    """
    Exception raised if none of the methods to mount the external
    source location which contains the Azure Li/VLi config file
    were successful
    """


class AzureHostedCommandException(AzureHostedException):
    """
    Exception raised if an external command called via a Command
    instance has returned with an exit code != 0 or could not
    be called at all.
    """


class AzureHostedCommandNotFoundException(AzureHostedException):
    """
    Exception raised if any executable command cannot be found in
    the evironment PATH variable.
    """


class AzureHostedNetworkConfigDataException(AzureHostedException):
    """
    Exception raised if any of the required data to setup the network
    configuration is missing
    """


class AzureHostedUserConfigDataException(AzureHostedException):
    """
    Exception raised if any of the required data to setup the user
    is missing
    """


class AzureHostedInstallException(AzureHostedException):
    """
    Exception raised if any of the required data to install
    packages is missing
    """


class AzureHostedMachineConstraintException(AzureHostedException):
    """
    Exception raised if any of the provided machine constraints
    violates the given constraint value
    """


class AzureHostedStorageMountException(AzureHostedException):
    """
    Exception raised if any of the required data to create a valid
    fstab entry to mount some storage device is missing
    """
