from treadmill.infra import vpc
from treadmill.infra import instances
from treadmill.infra import configuration
from treadmill.infra import constants
from treadmill.infra import subnet
import logging

_LOGGER = logging.getLogger(__name__)


class Cell:
    def __init__(self, domain, subnet_id=None, vpc_id=None):
        self.subnet_id = subnet_id
        if self.subnet_id:
            self.subnet = subnet.Subnet(id=self.subnet_id, vpc_id=vpc_id)
        self.vpc = vpc.VPC(id=vpc_id, domain=domain)
        self.domain = domain

    def setup_vpc(
            self,
            vpc_cidr_block,
            subnet_cidr_block,
            secgroup_name,
            secgroup_desc
    ):
        if not self.vpc.id:
            self.vpc.create(vpc_cidr_block)

        gateway_id = self.vpc.create_internet_gateway()
        if not self.subnet_id:
            self.vpc.create_subnet(
                subnet_cidr_block,
                gateway_id=gateway_id,
                name=constants.TREADMILL_CELL_SUBNET_NAME
            )
        self.subnet = self.vpc.subnets[-1]
        self.subnet_id = self.subnet.id
        self.vpc.create_security_group(secgroup_name, secgroup_desc)
        self.vpc.create_hosted_zone()
        self.vpc.create_hosted_zone(reverse=True)
        self.vpc.associate_dhcp_options()

    def setup_master(self, name, key_name, count, image_id, instance_type,
                     tm_release, ipa_hostname, app_root):
        if not self.subnet:
            raise('subnet_id required!')
        self.master_configuration = configuration.MasterConfiguration(
            self.domain,
            self.subnet.id,
            app_root,
            ipa_hostname,
            tm_release
        )

        _instances = instances.Instances.create(
            name=name,
            image_id=image_id,
            count=count,
            instance_type=instance_type,
            subnet_id=self.subnet.id,
            secgroup_ids=self.vpc.secgroup_ids,
            key_name=key_name,
            user_data=self.master_configuration.get_userdata(),
        )

        for instance in _instances.instances:
            instance.upsert_dns_record(
                self.vpc.hosted_zone_id,
                self.domain
            )
            instance.upsert_dns_record(
                self.vpc.reverse_hosted_zone_id,
                self.domain,
                reverse=True
            )

        self.subnet.instances = _instances
        self.ids = _instances.ids
        self.show()

        return self.vpc.id

    def destroy(self):
        self.vpc.get_hosted_zone_ids()
        self.subnet.destroy(
            hosted_zone_id=self.vpc.hosted_zone_id,
            reverse_hosted_zone_id=self.vpc.reverse_hosted_zone_id,
            domain=self.domain
        )

    def show(self):
        self.output = self.subnet.show()
        _LOGGER.info("******************************************************")
        _LOGGER.info(self.output)
        _LOGGER.info("******************************************************")
