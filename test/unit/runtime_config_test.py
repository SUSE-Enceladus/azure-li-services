from pytest import raises
from unittest.mock import patch
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.instance_type import InstanceType

from azure_li_services.exceptions import AzureHostedConfigDataException


class TestRuntimeConfig(object):
    def setup(self):
        self.runtime_config = RuntimeConfig('../data/config.yaml')

    @patch('yaml.load')
    def test_init_raises_on_invalid_format(self, mock_yaml_load):
        mock_yaml_load.side_effect = Exception
        with raises(AzureHostedConfigDataException):
            RuntimeConfig('../data/config.yaml')

    def test_init_raises_on_schema_validation(self):
        with raises(AzureHostedConfigDataException):
            RuntimeConfig('../data/config_invalid.yaml')

    def test_get_config_file_version(self):
        assert self.runtime_config.get_config_file_version().isoformat() == \
            '2017-11-15'

    def test_get_instance_type(self):
        assert self.runtime_config.get_instance_type() == InstanceType.li
        self.runtime_config.config_data['instance_type'] = 'VeryLargeInstance'
        assert self.runtime_config.get_instance_type() == InstanceType.vli

    def test_get_network_config(self):
        assert self.runtime_config.get_network_config() == [
            {
                'interface': 'eth0',
                'vlan': 10,
                'subnet_mask': '255.255.255.0',
                'ip': '10.250.10.51',
                'gateway': '10.250.10.1'
            }
        ]

    def test_get_user_config(self):
        assert self.runtime_config.get_user_config() == [
            {
                'ssh-key': 'ssh-rsa foo',
                'username': 'hanauser',
                'shadow_hash': 'sha-512-cipher'
            },
            {
                'group': 'nogroup',
                'home_dir': '/var/lib/empty',
                'username': 'rpc',
                'id': 495
            }
        ]

    def test_get_call_script(self):
        assert self.runtime_config.get_call_script() == \
            'path/to/executable/file'

    def test_get_packages_config(self):
        assert self.runtime_config.get_packages_config() == {
            'directory': [
                'directory-with-rpm-files',
                'another-directory-with-rpm-files'
            ],
            'repository_name': 'azure_packages'
        }

    def test_get_machine_constraints(self):
        assert self.runtime_config.get_machine_constraints() == {
            'min_cores': 32,
            'min_memory': '20tb'
        }

    def test_get_storage_config(self):
        assert self.runtime_config.get_storage_config() == [
            {
                'device': '10.250.21.12:/nfs/share',
                'min_size': '112G',
                'file_system': 'nfs',
                'mount': '/mnt/foo',
                'mount_options': ['a', 'b', 'c']
            }
        ]
