from treadmill.infra import vpc


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
        _vpc = vpc.VPC(domain=domain, region_name=region_name)
        _vpc.create(cidr_block=vpc_cidr_block)
        _vpc.create_subnet(
            cidr_block=subnet_cidr_block,
            region_name=region_name
        )
        _vpc.create_internet_gateway()
        _vpc.create_route_table()
        _vpc.create_security_group(
            GroupName=security_group_name,
            Description=security_group_description
        )
        _vpc.create_hosted_zone(Region=region_name)
