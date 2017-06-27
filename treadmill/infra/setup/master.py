from treadmill.infra.vpc import VPC
from treadmill.infra.instances import Instances


class Master:
    def __init__(
            self,
            vpc_id=None,
            domain='tw.treadmill',
            app_root='/var/tmp'
    ):
        self.vpc = VPC(vpc_id, domain=domain)
        self.domain = domain
        self.app_root = app_root

    def setup(
            self,
            tm_release='0.1.0',
            freeipa_hostname='treadmillfreeipa'
    ):
        if not self.vpc.id:
            self.vpc.create()

        self.vpc.create_subnet()
        self.vpc.create_internet_gateway()
        self.vpc.create_route_table()
        self.vpc.create_security_group('sg_common', 'Treadmill Security group')
        self.vpc.create_hosted_zone()
        self.vpc.associate_dhcp_options()

        self.setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': self.domain,
                    'NAME': 'TreadmillMaster',
                },
            },
            {'name': 'install-pid1.sh', 'vars': {}},
            {'name': 'install-s6.sh', 'vars': {}},
            {
                'name': 'configure-master.sh',
                'vars': {
                    'DOMAIN': self.domain,
                    'CELL': self.vpc.subnet_ids[0],
                    'APPROOT': self.app_root,
                    'FREEIPA_HOSTNAME': freeipa_hostname,
                    'TREADMILL_RELEASE': tm_release,
                },
            },
        ]

        instances = Instances.create_master(
            Name='TreadmillMaster',
            ImageId='ami-6d1c2007',
            Count=1,
            SubnetId=self.vpc.subnet_ids[0],
            SecurityGroupIds=self.vpc.secgroup_ids,
            SetupScripts=self.setup_scripts,
        )

        self.vpc.instance_ids = instances.ids
        self.ids = instances.ids
        self.show()

        return self.vpc.id

    def destroy(self):
        try:
            self.vpc.terminate_instances()
        except Exception as ex:
            print("Error: {0}".format(ex))

        self.vpc.delete_internet_gateway()
        self.vpc.delete_security_groups()
        self.vpc.delete_route_tables()
        self.vpc.delete()
        self.vpc.delete_hosted_zone()

    def show(self):
        self.output = self.vpc.show()
        print("******************************************************")
        print(self.output)
        print("******************************************************")
