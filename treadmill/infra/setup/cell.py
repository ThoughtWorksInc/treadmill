from treadmill.infra import vpc
from treadmill.infra import instances
from treadmill.infra import configuration
import logging

_LOGGER = logging.getLogger(__name__)


class Cell:
    def __init__(self, region_name, domain, subnet_id=None, vpc_id=None):
        self.vpc = vpc.VPC(region_name=region_name, id=vpc_id, domain=domain)
        self.subnet_id = subnet_id
        self.domain = domain
        self.region_name = region_name

    def setup_vpc(
            self,
            vpc_cidr_block,
            cell_cidr_block,
            secgroup_name,
            secgroup_desc
    ):
        if not self.vpc.id:
            self.vpc.create(vpc_cidr_block)

        self.vpc.create_subnet(self.region_name, cell_cidr_block)
        self.vpc.create_internet_gateway()
        self.vpc.create_route_table()
        self.vpc.create_security_group(secgroup_name, secgroup_desc)
        self.vpc.create_hosted_zone(region_name=self.region_name)
        self.vpc.create_hosted_zone(region_name=self.region_name, reverse=True)
        self.vpc.associate_dhcp_options()

    def setup_master(self, name, key_name, count, image_id, instance_type,
                     tm_release, ipa_hostname, app_root):
        self.master_configuration = configuration.MasterConfiguration(
            self.domain,
            self.subnet_id,
            app_root,
            ipa_hostname,
            tm_release
        )

        _instances = instances.Instances.create_master(
            name=name,
            image_id=image_id,
            count=count,
            instance_type=instance_type,
            subnet_id=self.subnet_id,
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
