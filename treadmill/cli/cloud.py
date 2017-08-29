import os
import click
from pprint import pprint
import logging

from treadmill.infra import constants, connection, vpc, subnet
from treadmill.infra.setup import ipa, ldap, node, cell
from treadmill.infra.utils import security_group, hosted_zones
from treadmill.cli import validate_ipa_password, ipa_password_prompt
from treadmill.cli import validate_domain


import yaml
from click import Option, UsageError

_LOGGER = logging.getLogger(__name__)

_OPTIONS_FILE = 'manifest'


def init():
    """Cloud CLI module"""
    @click.group()
    @click.option('--domain', required=True,
                  envvar='TREADMILL_DNS_DOMAIN',
                  callback=validate_domain,
                  help='Domain for hosted zone')
    @click.pass_context
    def cloud(ctx, domain):
        """Manage Treadmill on cloud"""
        ctx.obj['DOMAIN'] = domain

    class MutuallyExclusiveOption(Option):
        def __init__(self, *args, **kwargs):
            self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
            help = kwargs.get('help', '')
            if self.mutually_exclusive:
                ex_str = ', '.join(self.mutually_exclusive)
                kwargs['help'] = help + (
                    ' NOTE: This argument is mutually exclusive with'
                    ' arguments: [' + ex_str + '].'
                )
            super().__init__(*args, **kwargs)

        def handle_parse_result(self, ctx, opts, args):
            if self.mutually_exclusive.intersection(opts) and \
               self.name in opts:
                raise UsageError(
                    "Illegal usage: `{}` is mutually exclusive with "
                    "arguments `{}`.".format(
                        self.name,
                        ', '.join(self.mutually_exclusive)
                    )
                )
            if self.name == _OPTIONS_FILE and self.name in opts:
                _file = opts.pop(_OPTIONS_FILE)
                for _param in ctx.command.params:
                    opts[_param.name] = _param.default or \
                        _param.value_from_envvar(ctx) or ''
                with open(_file, 'r') as stream:
                    data = yaml.load(stream)

                opts.update(data)
                ctx.params = opts

            return super().handle_parse_result(ctx, opts, args)

    @cloud.group()
    def init():
        """Initialize Treadmill EC2 Objects"""
        pass

    @init.command(name='vpc')
    @click.option('--region', help='Region for the vpc')
    @click.option('--vpc-cidr-block', default='172.23.0.0/16',
                  help='CIDR block for the vpc')
    @click.option('--secgroup_name', default='sg_common',
                  help='Security group name')
    @click.option(
        '--secgroup_desc',
        default='Treadmill Security Group',
        help='Description for the security group'
    )
    @click.option('-m', '--' + _OPTIONS_FILE,
                  cls=MutuallyExclusiveOption,
                  mutually_exclusive=['region',
                                      'vpc_cidr_block',
                                      'secgroup_desc',
                                      'secgroup_name'],
                  help="Options YAML file. ")
    @click.pass_context
    def init_vpc(ctx, region, vpc_cidr_block,
                 secgroup_name, secgroup_desc, manifest):
        """Initialize Treadmill VPC"""
        domain = ctx.obj['DOMAIN']

        if region:
            connection.Connection.context.region_name = region

        connection.Connection.context.domain = domain

        _vpc = vpc.VPC.setup(
            cidr_block=vpc_cidr_block,
            secgroup_name=secgroup_name,
            secgroup_desc=secgroup_desc
        )

        click.echo(
            pprint(_vpc.show())
        )

    @init.command(name='ldap')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--region', help='Region for the vpc')
    @click.option('--key', required=True, help='SSH Key Name')
    @click.option('--count', default='1', type=int,
                  help='Number of Treadmill ldap instances to spin up')
    @click.option('--image', required=True,
                  help='Image to use for instances e.g. RHEL-7.4')
    @click.option('--instance-type',
                  default=constants.INSTANCE_TYPES['EC2']['micro'],
                  help='AWS ec2 instance type')
    # TODO: Pick the current Treadmill release by default.
    @click.option('--tm-release', default='0.1.0',
                  help='Treadmill release to use')
    @click.option('--ldap-hostname', default='treadmillldap1',
                  help='LDAP hostname')
    @click.option('--app-root', default='/var/tmp',
                  help='Treadmill app root')
    @click.option('--ldap-cidr-block', default='172.23.1.0/24',
                  help='CIDR block for LDAP')
    @click.option('--ldap-subnet-id', help='Subnet ID for LDAP')
    @click.option('--cell-subnet-id', help='Subnet ID of Cell')
    @click.option('--ipa-admin-password', callback=ipa_password_prompt,
                  envvar='TREADMILL_IPA_ADMIN_PASSWORD',
                  help='Password for IPA admin')
    @click.option('-m', '--' + _OPTIONS_FILE,
                  cls=MutuallyExclusiveOption,
                  mutually_exclusive=['region',
                                      'vpc_id',
                                      'key',
                                      'count',
                                      'image',
                                      'instance_type',
                                      'tm_release',
                                      'ldap_hostname',
                                      'app_root',
                                      'ldap_subnet_id',
                                      'cell_subnet_id',
                                      'ipa_admin_password'
                                      'ldap_cidr_block'],
                  help="Options YAML file. ")
    @click.pass_context
    def init_ldap(ctx, vpc_id, region, key, count, image,
                  instance_type, tm_release, ldap_hostname, app_root,
                  ldap_cidr_block, ldap_subnet_id, cell_subnet_id,
                  ipa_admin_password, manifest):
        """Initialize Treadmill LDAP"""

        domain = ctx.obj['DOMAIN']
        if region:
            connection.Connection.context.region_name = region

        connection.Connection.context.domain = domain

        _ldap = ldap.LDAP(
            name='TreadmillLDAP',
            vpc_id=vpc_id,
        )

        _ldap.setup(
            key=key,
            count=1,
            image=image,
            instance_type=instance_type,
            tm_release=tm_release,
            app_root=app_root,
            ldap_hostname=ldap_hostname,
            cidr_block=ldap_cidr_block,
            cell_subnet_id=cell_subnet_id,
            subnet_id=ldap_subnet_id,
            ipa_admin_password=ipa_admin_password,
        )

        click.echo(
            pprint(_ldap.subnet.show())
        )

    @init.command(name='cell')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--region', help='Region for the vpc')
    @click.option('--name', default='TreadmillMaster',
                  help='Treadmill master name')
    @click.option('--key', required=True, help='SSH Key Name')
    @click.option('--count', default='3', type=int,
                  help='Number of Treadmill masters to spin up')
    @click.option('--image', required=True,
                  help='Image to use for new instances e.g. RHEL-7.4')
    @click.option('--instance-type',
                  default=constants.INSTANCE_TYPES['EC2']['micro'],
                  help='AWS ec2 instance type')
    # TODO: Pick the current Treadmill release by default.
    @click.option('--tm-release', default='0.1.0',
                  help='Treadmill release to use')
    @click.option('--ldap-hostname', default='treadmillldap1',
                  help='LDAP hostname')
    @click.option('--app-root', default='/var/tmp', help='Treadmill app root')
    @click.option('--cell-cidr-block', default='172.23.0.0/24',
                  help='CIDR block for the cell')
    @click.option('--ldap-cidr-block', default='172.23.1.0/24',
                  help='CIDR block for LDAP')
    @click.option('--subnet-id', help='Subnet ID')
    @click.option('--ldap-subnet-id',
                  help='Subnet ID for LDAP')
    @click.option('--without-ldap', required=False, is_flag=True,
                  default=False, help='Flag for LDAP Server')
    @click.option('--ipa-admin-password', callback=ipa_password_prompt,
                  envvar='TREADMILL_IPA_ADMIN_PASSWORD',
                  help='Password for IPA admin')
    @click.option('-m', '--' + _OPTIONS_FILE,
                  cls=MutuallyExclusiveOption,
                  mutually_exclusive=['region',
                                      'vpc_id',
                                      'name',
                                      'key',
                                      'count',
                                      'image',
                                      'instance_type',
                                      'tm_release',
                                      'ldap_hostname',
                                      'app_root',
                                      'cell_cidr_block'
                                      'ldap_subnet_id',
                                      'subnet_id',
                                      'ipa_admin_password',
                                      'without_ldap',
                                      'ldap_cidr_block'],
                  help="Options YAML file. ")
    @click.pass_context
    def init_cell(ctx, vpc_id, region, name, key, count, image,
                  instance_type, tm_release, ldap_hostname, app_root,
                  cell_cidr_block, ldap_cidr_block, subnet_id, ldap_subnet_id,
                  without_ldap, ipa_admin_password, manifest):
        """Initialize Treadmill Cell"""

        domain = ctx.obj['DOMAIN']

        if region:
            connection.Connection.context.region_name = region

        connection.Connection.context.domain = domain

        _cell = cell.Cell(
            vpc_id=vpc_id,
            subnet_id=subnet_id,
        )

        result = {}
        if not without_ldap:
            _ldap = ldap.LDAP(
                name='TreadmillLDAP',
                vpc_id=vpc_id,
            )

            _ldap.setup(
                key=key,
                count=1,
                image=image,
                instance_type=instance_type,
                tm_release=tm_release,
                app_root=app_root,
                ldap_hostname=ldap_hostname,
                cidr_block=ldap_cidr_block,
                cell_subnet_id=_cell.id,
                subnet_id=ldap_subnet_id,
                ipa_admin_password=ipa_admin_password,
            )

            result['Ldap'] = _ldap.subnet.show()

        _cell.setup_zookeeper(
            name='TreadmillZookeeper',
            key=key,
            image=image,
            instance_type=instance_type,
            subnet_cidr_block=cell_cidr_block,
            ldap_hostname=ldap_hostname,
            ipa_admin_password=ipa_admin_password
        )

        _cell.setup_master(
            name=name,
            key=key,
            count=count,
            image=image,
            instance_type=instance_type,
            tm_release=tm_release,
            ldap_hostname=ldap_hostname,
            app_root=app_root,
            subnet_cidr_block=cell_cidr_block,
            ipa_admin_password=ipa_admin_password
        )

        result['Cell'] = _cell.show()

        click.echo(
            pprint(result)
        )

    @init.command(name='domain')
    @click.option('--name', default='TreadmillIPA',
                  help='Name of the instance')
    @click.option('--region', help='Region for the vpc')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--subnet-cidr-block', help='Cidr block of subnet for IPA',
                  default='172.23.2.0/24')
    @click.option('--subnet-id', help='Subnet ID')
    @click.option('--count', help='Count of the instances', default=1)
    @click.option('--ipa-admin-password', callback=validate_ipa_password,
                  envvar='TREADMILL_IPA_ADMIN_PASSWORD',
                  help='Password for IPA admin')
    @click.option('--tm-release', default='0.1.0', help='Treadmill Release')
    @click.option('--key', required=True, help='SSH key name')
    @click.option('--instance-type',
                  default=constants.INSTANCE_TYPES['EC2']['medium'],
                  help='Instance type')
    @click.option('--image', required=True,
                  help='Image to use for new master instance e.g. RHEL-7.4')
    @click.option('-m', '--' + _OPTIONS_FILE,
                  cls=MutuallyExclusiveOption,
                  mutually_exclusive=['region',
                                      'vpc_id',
                                      'name',
                                      'key',
                                      'count',
                                      'image',
                                      'instance_type',
                                      'tm_release',
                                      'subnet_cidr_block'
                                      'subnet_id',
                                      'ipa_admin_password'],
                  help="Options YAML file. ")
    @click.pass_context
    def init_domain(ctx, name, region, vpc_id, subnet_cidr_block, subnet_id,
                    count, ipa_admin_password, tm_release, key,
                    instance_type, image, manifest):
        """Initialize Treadmill Domain (IPA)"""

        domain = ctx.obj['DOMAIN']

        connection.Connection.context.domain = domain
        if region:
            connection.Connection.context.region_name = region

        if not ipa_admin_password:
            ipa_admin_password = os.environ.get(
                'TREADMILL_IPA_ADMIN_PASSWORD',
                click.prompt(
                    'Create IPA admin password ',
                    hide_input=True,
                    confirmation_prompt=True
                )
            )

        _ipa = ipa.IPA(name=name, vpc_id=vpc_id)
        _ipa.setup(
            subnet_id=subnet_id,
            count=count,
            ipa_admin_password=ipa_admin_password,
            tm_release=tm_release,
            key=key,
            instance_type=instance_type,
            image=image,
            cidr_block=subnet_cidr_block,
        )

        click.echo(
            pprint(_ipa.show())
        )

    @init.command(name='node')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--region', help='Region for the vpc')
    @click.option('--name', default='TreadmillNode',
                  help='Node name')
    @click.option('--key', required=True, help='SSH Key Name')
    @click.option('--count', default='1', type=int,
                  help='Number of Treadmill nodes to spin up')
    @click.option('--image', required=True,
                  help='Image to use for new node instance e.g. RHEL-7.4')
    @click.option('--instance-type',
                  default=constants.INSTANCE_TYPES['EC2']['large'],
                  help='AWS ec2 instance type')
    @click.option('--tm-release', default='0.1.0',
                  help='Treadmill release to use')
    @click.option('--ldap-hostname', default='treadmillldap1',
                  help='LDAP hostname')
    @click.option('--app-root', default='/var/tmp/treadmill-node',
                  help='Treadmill app root')
    @click.option('--subnet-id', required=True, help='Subnet ID')
    @click.option('--ipa-admin-password', callback=ipa_password_prompt,
                  envvar='TREADMILL_IPA_ADMIN_PASSWORD',
                  help='Password for IPA admin')
    @click.option('--with-api', required=False, is_flag=True,
                  default=False, help='Provision node with Treadmill APIs')
    @click.option('-m', '--' + _OPTIONS_FILE,
                  cls=MutuallyExclusiveOption,
                  mutually_exclusive=['region',
                                      'vpc_id',
                                      'name',
                                      'key',
                                      'count',
                                      'image',
                                      'instance_type',
                                      'tm_release',
                                      'ldap_hostname',
                                      'app_root',
                                      'subnet_id',
                                      'ipa_admin_password'
                                      'with_api'],
                  help="Options YAML file. ")
    @click.pass_context
    def init_node(ctx, vpc_id, region, name, key, count, image,
                  instance_type, tm_release, ldap_hostname, app_root,
                  subnet_id, ipa_admin_password, with_api, manifest):
        """Initialize new Node in Cell"""

        domain = ctx.obj['DOMAIN']

        connection.Connection.context.domain = domain
        if region:
            connection.Connection.context.region_name = region

        if not ipa_admin_password:
            ipa_admin_password = os.environ.get(
                'TREADMILL_IPA_ADMIN_PASSWORD',
                click.prompt('IPA admin password ', hide_input=True)
            )

        _node = node.Node(name, vpc_id)
        _node.setup(
            key=key,
            count=count,
            image=image,
            instance_type=instance_type,
            tm_release=tm_release,
            app_root=app_root,
            ldap_hostname=ldap_hostname,
            subnet_id=subnet_id,
            ipa_admin_password=ipa_admin_password,
            with_api=with_api,
        )
        click.echo(
            pprint(_node.subnet.show())
        )

    @cloud.group()
    def delete():
        """Delete Treadmill EC2 Objects"""
        pass

    @delete.command(name='vpc')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.pass_context
    def delete_vpc(ctx, vpc_id):
        """Delete VPC"""

        domain = ctx.obj['DOMAIN']
        connection.Connection.context.domain = domain

        vpc.VPC(id=vpc_id).delete()

    @delete.command(name='cell')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--subnet-id', required=True, help='Subnet ID of cell')
    @click.pass_context
    def delete_cell(ctx, vpc_id, subnet_id):
        """Delete Cell (Subnet)"""
        domain = ctx.obj['DOMAIN']
        connection.Connection.context.domain = domain
        _vpc = vpc.VPC(id=vpc_id)
        _vpc.load_hosted_zone_ids()
        subnet.Subnet(id=subnet_id).destroy(
            hosted_zone_id=_vpc.hosted_zone_id,
            reverse_hosted_zone_id=_vpc.reverse_hosted_zone_id
        )

    @delete.command(name='domain')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--subnet-id', required=True, help='Subnet ID of IPA')
    @click.option('--name', help='Name of Instance',
                  default="TreadmillIPA")
    @click.pass_context
    def delete_domain(ctx, vpc_id, subnet_id, name):
        """Delete IPA"""
        domain = ctx.obj['DOMAIN']
        connection.Connection.context.domain = domain

        _ipa = ipa.IPA(name=name, vpc_id=vpc_id)
        _ipa.destroy(subnet_id=subnet_id)

    @delete.command(name='ldap')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--subnet-id', required=True, help='Subnet ID of LDAP')
    @click.option('--name', help='Name of Instance',
                  default="TreadmillLDAP")
    @click.pass_context
    def delete_ldap(ctx, vpc_id, subnet_id, name):
        """Delete LDAP"""
        domain = ctx.obj['DOMAIN']
        connection.Connection.context.domain = domain

        _ldap = ldap.LDAP(name=name, vpc_id=vpc_id)
        _ldap.destroy(subnet_id=subnet_id)

    @delete.command(name='node')
    @click.option('--vpc-id', required=True, help='VPC ID of cell')
    @click.option('--name', help='Instance Name', required=False)
    @click.option('--instance-id', help='Instance ID', required=False)
    @click.pass_context
    def delete_node(ctx, vpc_id, name, instance_id):
        """Delete Node"""
        domain = ctx.obj['DOMAIN']
        if not name and not instance_id:
            _LOGGER.error('Provide either --name or --instance-id of'
                          'Node Instance and try again.')
            return

        connection.Connection.context.domain = domain
        _node = node.Node(name=name, vpc_id=vpc_id)
        _node.destroy(instance_id=instance_id)

    @cloud.group()
    def list():
        """Show Treadmill Cloud Resources"""
        pass

    @list.command(name='vpc')
    @click.option('--vpc-id', help='VPC ID of cell')
    @click.pass_context
    def vpc_resources(ctx, vpc_id):
        """Show VPC(s)"""
        domain = ctx.obj['DOMAIN']
        connection.Connection.context.domain = domain
        if vpc_id:
            result = pprint(vpc.VPC(id=vpc_id).show())
        else:
            result = vpc.VPC.all()
            result = "\n".join(result)

        click.echo(result)

    @list.command(name='cell')
    @click.option('--vpc-id', help='VPC ID of cell')
    @click.option('--subnet-id', help='Subnet ID of cell')
    @click.pass_context
    def cell_resources(ctx, vpc_id, subnet_id):
        """Show Cell"""
        domain = ctx.obj['DOMAIN']
        connection.Connection.context.domain = domain
        if subnet_id:
            click.echo(
                pprint(
                    subnet.Subnet(id=subnet_id).show()
                )
            )
            return

        if vpc_id:
            vpcs = [vpc_id]
        else:
            vpcs = vpc.VPC.all()

        result = []

        for v in vpcs:
            subnets = vpc.VPC(id=v).list_cells()
            if subnets:
                result.append({
                    'VpcId': v,
                    'Subnets': subnets
                })

        click.echo(pprint(result))

    @cloud.group()
    def port():
        """enable/disable EC2 instance port"""
        pass

    @port.command(name='enable')
    @click.option('--protocol', help='Protocol', default='tcp')
    @click.option('-p', '--port', required=True, help='Port')
    @click.option('-s', '--security-group-id', required=True,
                  help='Security Group ID')
    def enable_port(security_group_id, port, protocol):
        """Enable Port from my ip"""
        security_group.enable(port, security_group_id, protocol)

    @port.command(name='disable')
    @click.option('--protocol', help='Protocol', default='tcp')
    @click.option('-p', '--port', required=True, help='Port')
    @click.option('-s', '--security-group-id', required=True,
                  help='Security Group ID')
    def disable_port(security_group_id, port, protocol):
        """Disable Port from my ip"""
        security_group.disable(port, security_group_id, protocol)

    @cloud.command(name='delete-hosted-zone')
    @click.option('--zones-to-retain', required=True,
                  help='Hosted Zone IDs to retain', multiple=True)
    def delete_hosted_zones(zones_to_retain):
        """Delete Hosted Zones"""
        hosted_zones.delete_obsolete(zones_to_retain)

    return cloud
