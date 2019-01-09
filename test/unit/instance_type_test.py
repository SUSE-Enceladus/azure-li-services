from azure_li_services.instance_type import InstanceType


class TestInstanceType(object):
    def test_instance_type_names(self):
        assert InstanceType.li == 'li'
        assert InstanceType.vli == 'vli'
        assert InstanceType.vli_gen3 == 'vli_gen3'
