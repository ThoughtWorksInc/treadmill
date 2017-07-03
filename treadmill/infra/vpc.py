from treadmill.infra import connection
from treadmill.infra import instances
from treadmill.infra import constants

import time


class VPC:
    def __init__(self, domain, region_name, id=None, metadata=None):
        self.conn = connection.Connection()
        self.id = id
        self.metadata = metadata
        self.domain = domain
        self.instances = []
        self.secgroup_ids = []
        self.route_table_ids = []
        self.route_related_ids = []
        self.gateway_ids = []
        self.subnet_ids = []
        self.association_ids = []
        self.hosted_zone_id = None
        self.reverse_hosted_zone_id = None
        self.hosted_zone_ids = []

    @classmethod
    def get(cls, vpc_id):
        _conn = connection.Connection()
        json = _conn.describe_vpcs(VpcIds=[vpc_id])['Vpcs'][0]
        return VPC(
            id=json['VpcId'],
            metadata=json,
            region_name=None,
            domain=None
        )

    def create(self, cidr_block):
        vpc_response = self.conn.create_vpc(CidrBlock=cidr_block)
        self.cidr_block = vpc_response['Vpc']['CidrBlock']
        self.id = vpc_response['Vpc']['VpcId']
        self.conn.create_tags(
            Resources=[self.id],
            Tags=[{
                'Key': 'Name',
                'Value': 'Treadmill-vpc'
            }]
        )
        self.conn.modify_vpc_attribute(VpcId=self.id,
                                       EnableDnsHostnames={
                                           'Value': True
                                       })

    def create_subnet(self, region_name, cidr_block):
        self.region_name = region_name
        subnet = self.conn.create_subnet(
            VpcId=self.id,
            CidrBlock=cidr_block,
            AvailabilityZone=self._availability_zone_for(region_name)
        )
        self.subnet_ids.append(subnet['Subnet']['SubnetId'])

    def create_internet_gateway(self):
        gateway = self.conn.create_internet_gateway()
        gateway_id = gateway['InternetGateway']['InternetGatewayId']
        self.gateway_ids.append(gateway_id)
        self.conn.attach_internet_gateway(
            InternetGatewayId=gateway_id,
            VpcId=self.id
        )

    def create_route_table(self):
        route_table = self.conn.create_route_table(VpcId=self.id)
        self.route_table_id = route_table['RouteTable']['RouteTableId']
        for gateway_id in self.gateway_ids:
            self.conn.create_route(
                RouteTableId=self.route_table_id,
                DestinationCidrBlock=constants.DESTINATION_CIDR_BLOCK,
                GatewayId=gateway_id
            )
        for subnet_id in self.subnet_ids:
            self.conn.associate_route_table(
                SubnetId=subnet_id,
                RouteTableId=self.route_table_id
            )

    def create_security_group(self, group_name, description):
        self.secgroup_ids.append(self.conn.create_security_group(
            VpcId=self.id,
            GroupName=group_name,
            Description=description
        )['GroupId'])

    def create_hosted_zone(self, region_name, reverse=False):
        if reverse:
            identifier = 'reverse_hosted_zone_id'
            name = self._reverse_domain_name()
        else:
            identifier = 'hosted_zone_id'
            name = self.domain

        if not getattr(self, identifier):
            _conn = connection.Connection(constants.ROUTE_53)
            _hosted_zone_id = _conn.create_hosted_zone(
                Name=name,
                VPC={
                    'VPCRegion': region_name,
                    'VPCId': self.id,
                },
                HostedZoneConfig={
                    'PrivateZone': True
                },
                CallerReference=str(int(time.time()))
            )['HostedZone']['Id']
            setattr(self, identifier, _hosted_zone_id)

    def get_hosted_zone_ids(self):
        _conn = connection.Connection('route53')
        hosted_zones = _conn.list_hosted_zones()['HostedZones']
        for hosted_zone in hosted_zones:
            _hosted_zone_id = hosted_zone['Id']
            hosted_zone_details = _conn.get_hosted_zone(
                Id=_hosted_zone_id
            )
            if self.id in [_vpc['VPCId']
                           for _vpc in hosted_zone_details['VPCs']]:
                if 'in-addr.arpa' in hosted_zone_details['HostedZone']['Name']:
                    self.reverse_hosted_zone_id = _hosted_zone_id
                else:
                    self.hosted_zone_id = _hosted_zone_id
                self.hosted_zone_ids.append(_hosted_zone_id)

    def delete_hosted_zones(self):
        if not self.hosted_zone_ids:
            self.get_hosted_zone_ids()
        _conn = connection.Connection(constants.ROUTE_53)

        for id in self.hosted_zone_ids:
            _conn.delete_hosted_zone(
                Id=id
            )

    def get_instances(self):
        if not self.instances:
            self.instances = instances.Instances.get(
                filters=self._filters()
            )

    def terminate_instances(self):
        if not self.instances:
            self.get_instances()
        if not self.hosted_zone_ids:
            self.get_hosted_zone_ids()

        self.instances.terminate(
            hosted_zone_id=self.hosted_zone_id,
            reverse_hosted_zone_id=self.reverse_hosted_zone_id,
            domain=self.domain
        )

    def get_security_group_ids(self):
        if not self.secgroup_ids:
            res = self.conn.describe_security_groups(
                Filters=self._filters()
            )
            self.secgroup_ids = [sg['GroupId'] for sg in res['SecurityGroups']
                                 if sg['GroupName'] != 'default']

    def delete_security_groups(self):
        self.get_security_group_ids()

        for secgroup_id in self.secgroup_ids:
            self.conn.delete_security_group(GroupId=secgroup_id)

    def get_route_related_ids(self):
        response = self.conn.describe_route_tables(Filters=self._filters())
        if not self.association_ids:
            self.association_ids = self._get_ids_from_associations(
                response['RouteTables'],
                'RouteTableAssociationId'
            )
        if not self.route_table_ids:
            self.route_table_ids = self._get_ids_from_associations(
                response['RouteTables'],
                'RouteTableId'
            )
        if not self.subnet_ids:
            self.subnet_ids = self._get_ids_from_associations(
                response['RouteTables'],
                'SubnetId')

    def delete_route_tables(self):
        if not self.route_related_ids:
            self.get_route_related_ids()

        for ass_id in self.association_ids:
            self.conn.disassociate_route_table(
                AssociationId=ass_id
            )
        for route_table_id in self.route_table_ids:
            self.conn.delete_route_table(
                RouteTableId=route_table_id
            )
        for subnet_id in self.subnet_ids:
            self.conn.delete_subnet(
                SubnetId=subnet_id
            )

    def get_internet_gateway_ids(self):
        if not self.gateway_ids:
            response = self.conn.describe_internet_gateways(
                Filters=[{
                    'Name': constants.ATTACHMENT_VPC_ID,
                    'Values': [self.id],
                }]
            )

            self.gateway_ids = [gw['InternetGatewayId']
                                for gw in response['InternetGateways']]

    def delete_internet_gateway(self):
        self.get_internet_gateway_ids()

        for gateway_id in self.gateway_ids:
            self.conn.detach_internet_gateway(
                VpcId=self.id,
                InternetGatewayId=gateway_id
            )
            self.conn.delete_internet_gateway(
                InternetGatewayId=gateway_id
            )

    def delete(self):
        self.conn.delete_vpc(VpcId=self.id)

    def show(self):
        self.get_instances()
        return {
            'VpcId': self.id,
            'Instances': list(map(
                self._instance_details,
                [i.metadata for i in self.instances.instances])
            )
        }

    def associate_dhcp_options(self, options=[]):
        _default_options = [
            {
                'Key': 'domain-name',
                'Values': [self.domain]
            },
            {
                'Key': 'domain-name-servers',
                'Values': ['AmazonProvidedDNS']
            }
        ]
        response = self.conn.create_dhcp_options(
            DhcpConfigurations=_default_options + options
        )

        self.dhcp_options_id = response['DhcpOptions']['DhcpOptionsId']
        self.conn.associate_dhcp_options(
            DhcpOptionsId=self.dhcp_options_id,
            VpcId=self.id
        )

    def _reverse_domain_name(self):
        cidr_block_octets = self.cidr_block.split('.')
        return '.'.join([
            cidr_block_octets[1],
            cidr_block_octets[0],
            constants.REVERSE_DNS_TLD
        ])

    def _instance_details(self, data):
        return {
            'Name': self._select_from_tags(data['Tags'], 'Name'),
            'InstanceId': data['InstanceId'],
            'InstanceState': data['State']['Name'],
            'SecurityGroups': data['SecurityGroups'],
            'SubnetId': data['SubnetId']
        }

    def _select_from_tags(self, tags, selector):
        for t in tags:
            if t['Key'] == selector:
                return t['Value']

    def _get_ids_from_associations(self, routes, key):
        return [
            _f.get(key) for _f in sum([_r['Associations'] for _r in routes],
                                      []) if _f.get(key) and not _f.get('Main')
        ]

    def _filters(self):
        return [{
            'Name': 'vpc-id',
            'Values': [self.id]
        }]

    def _availability_zone_for(self, region_name):
        _map = {
            "us-east-1": "us-east-1a",
            "us-east-2": "us-east-2a",
            "ap-southeast-1": "ap-southeast-1a",
            "ap-southeast-2": "ap-southeast-2a",
            "us-west-1": "us-west-1b",
            "us-west-2": "us-west-2a"
        }

        return _map.get(region_name, None)
