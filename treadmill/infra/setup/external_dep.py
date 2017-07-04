from treadmill.infra import instances
from treadmill.infra import connection
from treadmill.infra import vpc
from treadmill.infra import constants


class ExternalDep:
    def __init__(
            self,
            name,
            vpc_id,
            domain,
            region_name
    ):
        self.name = name
        self.vpc_id = vpc_id
        self.domain = domain
        self.region_name = region_name
        self.route_53_conn = connection.Connection('route53')

    def setup(
            self,
            image_id,
            count,
            cidr_block,
            subnet_id=None,
    ):
        self.vpc = vpc.VPC(
            id=self.vpc_id,
            domain=self.domain,
            region_name=self.region_name
        )
        self.vpc.get_hosted_zone_ids()

        if not subnet_id:
            self.vpc.create_subnet(self.region_name, cidr_block)
            subnet_id = self.vpc.subnet_ids[0]

        self.instances = instances.Instances.create(
            name=self.name,
            image_id=image_id,
            count=count,
            subnet_id=subnet_id,
            instance_type=constants.INSTANCE_TYPES['EC2']['medium']
        )

        for i in self.instances.instances:
            i.upsert_dns_record(
                self.vpc.hosted_zone_id,
                self.domain
            )
            i.upsert_dns_record(
                self.vpc.reverse_hosted_zone_id,
                self.domain,
                reverse=True
            )

    def destroy(self, instance_id):
        self.instances = instances.Instances.get(ids=[instance_id])
        self.vpc = vpc.VPC(
            id=self.vpc_id,
            domain=self.domain,
            region_name=self.region_name
        )
        self.vpc.get_hosted_zone_ids()

        self.instances.terminate(
            hosted_zone_id=self.vpc.hosted_zone_id,
            reverse_hosted_zone_id=self.vpc.reverse_hosted_zone_id,
            domain=self.domain
        )
