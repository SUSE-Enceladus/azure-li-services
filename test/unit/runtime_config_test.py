from azure_li_services.runtime_config import RuntimeConfig


class TestRuntimeConfig(object):
    def setup(self):
        self.runtime_config = RuntimeConfig('../data/config.yaml')

    def test_get_config_file_version(self):
        assert self.runtime_config.get_config_file_version().isoformat() == \
            '2017-11-15'
