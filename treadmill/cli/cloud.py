import click
from pprint import pprint
from treadmill.infra.setup.cell import Cell
from treadmill.infra import constants, connection, vpc, subnet


def init():
    """Cloud CLI module"""
    @click.group()
    def cloud():
        """Manage treadmill on cloud"""
        pass

    @cloud.command(name='init')
    @click.option('--vpc-id', required=False, help='VPC ID of cell')
    @click.option('--domain', required=False, default='ms.treadmill',
                  help='Domain for hosted zone')
    @click.option('--region', required=False,
                  help='Region for the vpc')
    @click.option('--vpc-cidr-block', required=False,
                  default='172.23.0.0/16', help='CIDR block for the vpc')
    @click.option('--secgroup_name', required=False,
                  default='sg_common', help='Security group name')
    @click.option(
        '--secgroup_desc',
        required=False,
        default='Treadmill Security Group',
        help='Description for the security group')
    def init(vpc_id, domain, region, vpc_cidr_block,
             secgroup_name, secgroup_desc):
        """Initialize treadmill VPC"""
        if region:
            connection.Connection.region_name = region

        cell = Cell(
            domain=domain,
            vpc_id=vpc_id
        )

        cell.setup_vpc(
            vpc_cidr_block=vpc_cidr_block,
            secgroup_name=secgroup_name,
            secgroup_desc=secgroup_desc,
        )
        click.echo(
            pprint(cell.vpc.show())
        )

    @cloud.command(name='init-cell')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--region', required=False, help='Region for the vpc')
    @click.option('--domain', required=False,
                  default='ms.treadmill', help='Domain for hosted zone')
    @click.option('--name', required=False, default='TreadmillMaster',
                  help='Treadmill master name')
    @click.option('--key', required=True, help='SSH Key Name')
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
    @click.option('--ldap-hostname', required=True,
                  default='ldapserver', help='LDAP hostname')
    @click.option('--app-root', required=True,
                  default='/var/tmp/', help='Treadmill app root')
    @click.option('--cell-cidr-block', required=False,
                  default='172.23.0.0/24', help='CIDR block for the cell')
    @click.option('--subnet-id', required=False, help='Subnet ID')
    def init_cell(vpc_id, region, domain, name, key, count, image_id,
                  instance_type, tm_release, ldap_hostname, app_root,
                  cell_cidr_block, subnet_id):
        """Initialize treadmill cell"""
        if region:
            connection.Connection.region_name = region

        cell = Cell(
            domain=domain,
            vpc_id=vpc_id,
            subnet_id=subnet_id,
        )

        cell.setup_master(
            name=name,
            key=key,
            count=count,
            image_id=image_id,
            instance_type=instance_type,
            tm_release=tm_release,
            ldap_hostname=ldap_hostname,
            app_root=app_root,
            subnet_cidr_block=cell_cidr_block,
        )

        cell.setup_ldap(
            name='TreadmillLDAP',
            key=key,
            image_id=image_id,
            instance_type=instance_type,
            tm_release=tm_release,
            app_root=app_root,
            ldap_hostname=ldap_hostname,
            subnet_cidr_block=cell_cidr_block,
        )

        click.echo(
            pprint(cell.show())
        )

    @cloud.command(name='delete-vpc')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--domain', required=True,
                  default='ms.treadmill', help='Domain for hosted zone')
    def delete_vpc(vpc_id, domain):
        """Delete VPC"""
        vpc.VPC(id=vpc_id, domain=domain).delete()

    @cloud.command(name='delete-cell')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--domain', required=True, default='ms.treadmill',
                  help='Domain for hosted zone')
    @click.option('--subnet-id', required=True, help='Subnet ID of cell')
    def delete_cell(vpc_id, domain, subnet_id):
        """Delete Subnet"""
        _vpc = vpc.VPC(id=vpc_id, domain=domain)
        _vpc.get_hosted_zone_ids()
        subnet.Subnet(id=subnet_id).destroy(
            hosted_zone_id=_vpc.hosted_zone_id,
            reverse_hosted_zone_id=_vpc.reverse_hosted_zone_id,
            domain=_vpc.domain
        )

    @cloud.command(name='list-vpc-resources')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--domain', required=True,
                  default='ms.treadmill', help='Domain for hosted zone')
    def list_vpc_resources(vpc_id, domain):
        """Show VPC"""
        return vpc.VPC(id=vpc_id, domain=domain).show()

    @cloud.command(name='list-cell-resources')
    @click.option('--subnet-id', required=True, help='Subnet ID of cell')
    def list_cell_resources(subnet_id):
        """Show Cell"""
        return subnet.Subnet(id=subnet_id).show()

    del init
    del init_cell
    del delete_vpc
    del delete_cell

    return cloud
