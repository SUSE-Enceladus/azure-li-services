from azure_li_services.version import __VERSION__


class TestVersion(object):
    def test_version(self):
        assert __VERSION__ is not None
