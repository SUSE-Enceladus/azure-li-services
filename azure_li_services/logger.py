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
import logging

# project
from azure_li_services.defaults import Defaults


class Logger:
    @staticmethod
    def setup():
        logger = logging.getLogger('Azure_LI_Services')
        logger.setLevel(logging.INFO)

        log_file = logging.FileHandler(Defaults.get_log_file())
        log_file.setLevel(logging.INFO)

        log_stream = logging.StreamHandler()
        log_stream.setLevel(logging.INFO)

        logger.addHandler(log_stream)
        logger.addHandler(log_file)
