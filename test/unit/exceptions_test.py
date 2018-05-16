from azure_li_services.exceptions import AzureHostedException


class TestAzureHostedException(object):
    def test_init(self):
        instance = AzureHostedException('message')
        assert instance.__str__() == 'message'
