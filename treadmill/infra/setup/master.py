from treadmill.infra import vpc
from treadmill.infra import instances
from treadmill.infra import configuration
from treadmill.infra import constants
import logging

_LOGGER = logging.getLogger(__name__)


class MasterConfiguration(configuration.Configuration):
    def __init__(self, domain, cell, app_root, freeipa_hostname, tm_release):
        self.setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': domain,
                    'NAME': 'TreadmillMaster',
                },
            },
            {'name': 'install-pid1.sh', 'vars': {}},
            {'name': 'install-s6.sh', 'vars': {}},
            {
                'name': 'configure-master.sh',
                'vars': {
                    'DOMAIN': domain,
                    'CELL': cell,
                    'APPROOT': app_root,
                    'FREEIPA_HOSTNAME': freeipa_hostname,
                    'TREADMILL_RELEASE': tm_release,
                },
            },
        ]
        super(MasterConfiguration, self).__init__(self.setup_scripts)


class Master:
    def __init__(
            self,
            vpc_id=None,
            domain='tw.treadmill',
            app_root='/var/tmp'
    ):
        self.vpc = vpc.VPC(vpc_id, domain=domain)
        self.domain = domain
        self.app_root = app_root

    def setup(
            self,
            tm_release='0.1.0',
            freeipa_hostname=constants.FREEIPA_HOSTNAME
    ):
        if not self.vpc.id:
            self.vpc.create()

        self.vpc.create_subnet()
        self.vpc.create_internet_gateway()
        self.vpc.create_route_table()
        self.vpc.create_security_group('sg_common', 'Treadmill Security group')
        self.vpc.create_hosted_zone()
        self.vpc.create_hosted_zone(Reverse=True)
        self.vpc.associate_dhcp_options()

        self.master_configuration = MasterConfiguration(
            self.domain,
            self.vpc.subnet_ids[0],
            self.app_root,
            freeipa_hostname,
            tm_release
        )

        _instances = instances.Instances.create_master(
            Name='TreadmillMaster',
            ImageId='ami-9e2f0988',
            Count=constants.MASTER_INSTANCES_COUNT,
            SubnetId=self.vpc.subnet_ids[0],
            SecurityGroupIds=self.vpc.secgroup_ids,
            UserData=self.master_configuration.get_userdata(),
        )

        for instance in _instances.instances:
            instance.upsert_dns_record(
                self.vpc.hosted_zone_id,
                self.domain
            )
            instance.upsert_dns_record(
                self.vpc.reverse_hosted_zone_id,
                self.domain,
                Reverse=True
            )

        self.vpc.instance_ids = _instances.ids
        self.ids = _instances.ids
        self.show()

        return self.vpc.id

    def destroy(self):
        self.vpc.terminate_instances()
        self.vpc.delete_internet_gateway()
        self.vpc.delete_security_groups()
        self.vpc.delete_route_tables()
        self.vpc.delete_hosted_zones()
        self.vpc.delete()

    def show(self):
        self.output = self.vpc.show()
        _LOGGER.info("******************************************************")
        _LOGGER.info(self.output)
        _LOGGER.info("******************************************************")
