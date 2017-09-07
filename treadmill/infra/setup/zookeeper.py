from treadmill.infra.setup import base_provision
from treadmill.infra import configuration, constants
from treadmill.infra import instances


class Zookeeper(base_provision.BaseProvision):
    def setup(self, image, key, cidr_block, instance_type, ldap_hostname,
              ipa_admin_password, subnet_id=None):
        ipa_server_hostname = instances.Instances.get(
            filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [self.vpc.id]
                },
                {
                    'Name': 'tag-key',
                    'Values': ['Role']
                },
                {
                    'Name': 'tag-value',
                    'Values': [constants.ROLES['IPA']]
                }
            ]
        ).instances[0].hostname

        self.configuration = configuration.Zookeeper(
            self.name,
            ldap_hostname,
            ipa_server_hostname
        )
        self.subnet_name = constants.TREADMILL_CELL_SUBNET_NAME
        super().setup(
            image=image,
            count=3,
            cidr_block=cidr_block,
            subnet_id=subnet_id,
            key=key,
            instance_type=instance_type
        )
