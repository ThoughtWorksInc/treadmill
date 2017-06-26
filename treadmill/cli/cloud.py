import click
from treadmill.infra.vpc import VPC
from treadmill.infra.setup.master import Master


def init():
    """Cloud CLI module"""
    @click.group()
    def cloud():
        """Manage treadmill on cloud"""
        pass

    @cloud.command(name='init')
    @click.option('--cell', required=False, is_flag=True,
                  help='Create a new treadmill cell')
    def init(cell):
        """Initialize treadmill cloud"""
        if cell:
            _master = Master()
            _master.setup()

        else:
            _vpc = VPC()
            _vpc.create()
            _vpc.create_subnet()
            _vpc.create_internet_gateway()
            _vpc.create_route_table()
            _vpc.create_security_group(
                'sg_common',
                'Treadmill Security group'
            )
            _vpc.create_hosted_zone()

    del init

    return cloud
