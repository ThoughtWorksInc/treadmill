import logging

from treadmill.infra import vpc, subnet
from treadmill.infra.setup import ldap, master

_LOGGER = logging.getLogger(__name__)


class Cell:
    def __init__(self, domain, subnet_id=None, vpc_id=None):
        self.domain = domain
        self.vpc = vpc.VPC(id=vpc_id, domain=self.domain)
        self.master = master.Master(
            name=None,
            vpc_id=self.vpc.id,
            domain=self.domain,
        )
        self.master.subnet = subnet.Subnet(id=subnet_id)
        self.id = subnet_id

    def setup_vpc(
            self,
            vpc_cidr_block,
            secgroup_name,
            secgroup_desc
    ):
        if not self.vpc.id:
            self.vpc.create(vpc_cidr_block)
        else:
            self.vpc.refresh()

        self.vpc.create_internet_gateway()
        self.vpc.create_security_group(secgroup_name, secgroup_desc)
        self.vpc.create_hosted_zone()
        self.vpc.create_hosted_zone(reverse=True)
        self.vpc.associate_dhcp_options()

    def setup_master(self, name, key, count, image_id, instance_type,
                     tm_release, ldap_hostname,
                     app_root, subnet_cidr_block=None):
        if not self.vpc.id:
            raise('Provide vpc_id in init or setup vpc prior.')

        self.master.vpc.id = self.vpc.id
        self.master.name = name
        self.master.setup(
            image_id=image_id,
            count=count,
            cidr_block=subnet_cidr_block,
            key=key,
            ldap_hostname=ldap_hostname,
            tm_release=tm_release,
            instance_type=instance_type,
            app_root=app_root,
            subnet_id=self.id
        )
        self.id = self.master.subnet.id
        self.show()

    def setup_ldap(self, name, key, image_id, instance_type,
                   tm_release, app_root, ldap_hostname,
                   subnet_cidr_block=None):
        self.ldap = ldap.LDAP(name, self.vpc.id, self.domain)
        self.ldap.setup(
            image_id=image_id,
            count=1,
            key=key,
            cidr_block=subnet_cidr_block,
            tm_release=tm_release,
            instance_type=instance_type,
            subnet_id=self.id,
            app_root=app_root,
            ldap_hostname=ldap_hostname
        )

    def destroy(self):
        self.vpc.get_hosted_zone_ids()
        self.master.subnet.destroy(
            hosted_zone_id=self.vpc.hosted_zone_id,
            reverse_hosted_zone_id=self.vpc.reverse_hosted_zone_id,
            domain=self.domain
        )

    def show(self):
        self.output = self.master.subnet.show()
        _LOGGER.info("******************************************************")
        _LOGGER.info(self.output)
        _LOGGER.info("******************************************************")
        return self.output
