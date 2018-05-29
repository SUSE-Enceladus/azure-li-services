#!/usr/bin/env python
import platform

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from azure_li_services.version import __VERSION__

python_version = platform.python_version().split('.')[0]

with open('.virtualenv.requirements.txt') as f:
    requirements = f.read().splitlines()

config = {
    'name': 'azure_li_services',
    'description': 'Azure Large Instance Services',
    'author': 'PubCloud Development team',
    'url': 'https://github.com/SUSE/azure-li-services',
    'download_url': 'https://github.com/SUSE/azure-li-services',
    'author_email': 'public-cloud-dev@susecloud.net',
    'version': __VERSION__,
    'install_requires': requirements,
    'packages': ['azure_li_services'],
    'entry_points': {
        'console_scripts': [
            'azure-li-config-lookup=azure_li_services.units.config_lookup:main',
            'azure-li-network=azure_li_services.units.network:main',
            'azure-li-user=azure_li_services.units.user:main'
        ]
    },
    'include_package_data': True,
    'license': 'GPLv3',
    'zip_safe': False,
    'classifiers': [
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Operating System'
    ]
}

setup(**config)
