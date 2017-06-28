import click
from treadmill.infra.setup.cell import Cell


def init():
    """Cloud CLI module"""
    @click.group()
    def cloud():
        """Manage treadmill on cloud"""
        pass

    @cloud.command(name='init')
    @click.option('--cell', required=False, is_flag=True,
                  help='Create a new treadmill cell')
    @click.option('--domain', required=False,
                  default='tw.treadmill', help='Domain for hosted zone')
    @click.option('--region', required=False,
                  default='us-east-1', help='Region for the vpc')
    @click.option('--vpc-cidr-block', required=False,
                  default='172.23.0.0/16', help='Cidr block for the vpc')
    @click.option('--subnet-cidr-block', required=False,
                  default='172.23.0.0/24', help='Cidr block for the subnet')
    @click.option('--security-group-name', required=False,
                  default='sg_common', help='Region for the vpc')
    @click.option(
        '--security-group-description',
        required=False,
        default='Treadmill Security Group',
        help='Description for the security group')
    def init(
        cell, domain, region, vpc_cidr_block,
        subnet_cidr_block, security_group_name,
        security_group_description
    ):
        """Initialize treadmill cloud"""
        cell = Cell()
        cell.vpc_setup(
            domain=domain,
            region_name=region,
            vpc_cidr_block=vpc_cidr_block,
            subnet_cidr_block=subnet_cidr_block,
            security_group_name=security_group_name,
            security_group_description=security_group_description
        )

    del init

    return cloud
