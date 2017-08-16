from treadmill.infra.setup import base_provision
from treadmill.infra import configuration, constants


class Zookeeper(base_provision.BaseProvision):
    def setup(self, image_id, key, cidr_block, instance_type, ldap_hostname,
              subnet_id=None):
        self.configuration = configuration.Zookeeper(
            self.name,
            ldap_hostname
        )
        self.subnet_name = constants.TREADMILL_CELL_SUBNET_NAME
        super().setup(
            image_id=image_id,
            count=3,
            cidr_block=cidr_block,
            subnet_id=subnet_id,
            key=key,
            instance_type=instance_type
        )
