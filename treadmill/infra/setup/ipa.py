import treadmill
from treadmill.infra.setup import base_provision
from treadmill.infra import configuration, constants
import polling


class IPA(base_provision.BaseProvision):
    def __init__(self, *args, **kwargs):
        self._instances = None

        super().__init__(*args, **kwargs)

    @property
    def instances(self):
        if not self._instances:
            self.subnet.refresh()
            self._instances = self.subnet.get_instances(
                refresh=True,
                role=constants.ROLES['IPA']
            )

        return self._instances

    def setup(
            self,
            image,
            count,
            cidr_block,
            ipa_admin_password,
            tm_release,
            key,
            instance_type,
            proid,
            subnet_name,
            subnet_id=None,
    ):
        treadmill.infra.get_iam_role(
            name=constants.IPA_EC2_IAM_ROLE,
            create=True
        )

        self.configuration = configuration.IPA(
            name=self.name,
            subnet_id=subnet_id,
            vpc=self.vpc,
            ipa_admin_password=ipa_admin_password,
            tm_release=tm_release,
            proid=proid
        )
        super().setup(
            image=image,
            count=count,
            cidr_block=cidr_block,
            subnet_id=subnet_id,
            key=key,
            instance_type=instance_type,
            subnet_name=subnet_name
        )

        def check_passed_status():
            return all(
                map(
                    lambda i: i.running_status(refresh=True) == 'passed',
                    self.instances.instances
                )
            )

        polling.poll(
            check_passed_status,
            step=10,
            timeout=600
        )
        self.vpc.associate_dhcp_options(default=True)
        self.vpc.delete_dhcp_options()
        self.vpc.associate_dhcp_options([
            {
                'Key': 'domain-name-servers',
                'Values': [
                    i.metadata['PrivateIpAddress']
                    for i in self.instances.instances
                ]
            }
        ])

    def destroy(self, subnet_id):
        super().destroy(
            subnet_id=subnet_id
        )
