import click
from treadmill.infra.setup.cell import Cell
from treadmill.infra import constants


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
        """Initialize treadmill VPC"""
        cell = Cell(
            region_name=region,
            domain=domain,
            vpc_id=vpc_id
        )

        cell.setup_vpc(
            cidr_block=vpc_cidr_block,
            secgroup_name=secgroup_name,
            secgroup_desc=secgroup_desc,
        )

    @cloud.command(name='init-cell')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--region', required=False,
                  default='us-east-1', help='Region for the vpc')
    @click.option('--domain', required=False,
                  default='ms.treadmill', help='Domain for hosted zone')
    @click.option('--name', required=False, default='TreadmillMaster',
                  help='Treadmill master name')
    @click.option('--key-name', required=True, help='Key name')
    @click.option('--count', required=True, default='3', type=int,
                  help='Number of treadmill masters to spin up')
    @click.option('--image-id', required=True,
                  help='AMI ID to use for new master instance')
    @click.option('--instance-type', required=True,
                  default=constants.INSTANCE_TYPES['EC2']['micro'],
                  help='AWS ec2 instance type')
    # TODO: Pick the current treadmill release by default.
    @click.option('--tm-release', required=True,
                  default='0.1.0', help='Treadmill release to use')
    @click.option('--ipa-hostname', required=True,
                  default='ipaserver', help='IPA hostname')
    @click.option('--app-root', required=True,
                  default='/var/tmp/', help='Treadmill app root')
    @click.option('--subnet-id', required=True, help='Subnet ID')
    def init_cell(vpc_id, region, domain, name, key_name, count, image_id,
                  instance_type, tm_release, ipa_hostname, app_root,
                  subnet_id):
        """Initialize treadmill cell"""
        cell = Cell(
            region_name=region,
            domain=domain,
            vpc_id=vpc_id,
            subnet_id=subnet_id,
        )

        cell.setup_master(
            name=name,
            key_name=key_name,
            count=count,
            image_id=image_id,
            instance_type=instance_type,
            tm_release=tm_release,
            ipa_hostname=ipa_hostname,
            app_root=app_root,
        )

    del init
    del init_cell

    return cloud
