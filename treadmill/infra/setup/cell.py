from treadmill.infra.vpc import VPC


class Cell:
    def __init__(self):
        pass

    def vpc_setup(
        self,
        domain='tw.treadmill',
        region_name='us-east-1',
        vpc_cidr_block='172.23.0.0/16',
        subnet_cidr_block='172.23.0.0/24',
        security_group_name='sg_common',
        security_group_description='Treadmill Security Group'
    ):
        vpc = VPC(domain=domain, region_name=region_name)
        vpc.create(cidr_block=vpc_cidr_block)
        vpc.create_subnet(
            cidr_block=subnet_cidr_block,
            region_name=region_name
        )
        vpc.create_internet_gateway()
        vpc.create_route_table()
        vpc.create_security_group(
            GroupName=security_group_name,
            Description=security_group_description
        )
        vpc.create_hosted_zone(Region=region_name)
