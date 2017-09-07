from treadmill.infra.setup import base_provision
from treadmill.infra import configuration, constants
from treadmill.infra import instances


class LDAP(base_provision.BaseProvision):
    def setup(
            self,
            image,
            count,
            key,
            cidr_block,
            tm_release,
            instance_type,
            app_root,
            ldap_hostname,
            cell_subnet_id,
            ipa_admin_password,
            subnet_id=None
    ):
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

        self.configuration = configuration.LDAP(
            cell_subnet_id=cell_subnet_id,
            ldap_hostname=ldap_hostname,
            tm_release=tm_release,
            app_root=app_root,
            name=self.name,
            ipa_admin_password=ipa_admin_password,
            ipa_server_hostname=ipa_server_hostname
        )
        super().setup(
            image=image,
            count=count,
            cidr_block=cidr_block,
            subnet_id=subnet_id,
            key=key,
            instance_type=instance_type
        )
