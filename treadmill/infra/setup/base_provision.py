from treadmill.infra import instances
from treadmill.infra import connection
from treadmill.infra import vpc
from treadmill.infra import constants
from treadmill.infra import cell


class BaseProvision:
    def __init__(
            self,
            name,
            vpc_id,
            domain,
    ):
        self.name = name
        self.vpc_id = vpc_id
        self.domain = domain
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
        )
        self.vpc.get_hosted_zone_ids()
        self.vpc.get_internet_gateway_ids()

        if not subnet_id:
            self.vpc.create_cell(
                cidr_block=cidr_block,
                name=self.name,
                gateway_id=self.vpc.gateway_ids[0]
            )
            subnet_id = self.vpc.subnets[-1].id

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

    def destroy(self, instance_id, subnet_id):
        self.instances = instances.Instances.get(ids=[instance_id])
        self.vpc = vpc.VPC(
            id=self.vpc_id,
            domain=self.domain
        )

        self.vpc.get_hosted_zone_ids()
        self.instances.terminate(
            hosted_zone_id=self.vpc.hosted_zone_id,
            reverse_hosted_zone_id=self.vpc.reverse_hosted_zone_id,
            domain=self.domain
        )
        cell.Cell(id=subnet_id).delete()
