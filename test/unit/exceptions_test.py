from azure_li_services.exceptions import AzureLiException


class TestAzureLiException(object):
    def test_init(self):
        instance = AzureLiException('message')
        assert instance.__str__() == 'message'
