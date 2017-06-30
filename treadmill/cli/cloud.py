import click
from treadmill.infra.setup.cell import Cell


def init():
    """Cloud CLI module"""
    @click.group()
    def cloud():
        """Manage treadmill on cloud"""
        pass

    @cloud.command(name='init')
    @click.option('--vpc-id', required=False, help='VPC ID of cell')
    @click.option('--domain', required=False,
                  default='ms.treadmill', help='Domain for hosted zone')
    @click.option('--region', required=False,
                  default='us-east-1', help='Region for the vpc')
    @click.option('--vpc-cidr-block', required=False,
                  default='172.23.0.0/16', help='CIDR block for the vpc')
    @click.option('--secgroup_name', required=False,
                  default='sg_common', help='Security group name')
    @click.option(
        '--secgroup_desc',
        required=False,
        default='Treadmill Security Group',
        help='Description for the security group')
    def init(vpc_id, domain, region, vpc_cidr_block, secgroup_name,
             secgroup_desc):
        """Initialize treadmill cell"""
        cell = Cell(
            region_name=region,
            domain=domain,
            vpc_id=vpc_id
        )

        cell.setup_vpc(
            vpc_cidr_block=vpc_cidr_block,
            secgroup_name=secgroup_name,
            secgroup_desc=secgroup_desc,
        )

    del init

    return cloud
