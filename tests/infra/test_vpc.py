"""
Unit test for VPC.
"""

import unittest
import mock

from treadmill.infra import vpc
from treadmill.infra.instances import Instance
from treadmill.infra.instances import Instances


class VPCTest(unittest.TestCase):
    """Tests supervisor routines."""

    def setUp(self):
        self.vpc_id_mock = '786'
        self.subnet_id_mock = '111'
        self.gateway_id_mock = '007'
        self.route_table_id_mock = '411'
        self.security_group_id_mock = '777'
        self.internet_gateway_id_mock = '999'

    @mock.patch('treadmill.infra.connection.Connection',
                mock.Mock(return_value='foo'))
    def test_init(self):
        _vpc = vpc.VPC()

        self.assertEquals(_vpc.conn, 'foo')
        self.assertIsNone(_vpc.id)

    @mock.patch('treadmill.infra.connection.Connection')
    def test_create(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.create_vpc = mock.Mock(
            return_value={'Vpc': {
                'VpcId': self.vpc_id_mock,
                'CidrBlock': '172.16.0.0/16'
            }}
        )
        _connectionMock.create_tags = mock.Mock()

        _vpc = vpc.VPC()
        _vpc.create()

        self.assertEquals(_vpc.id, self.vpc_id_mock)
        self.assertEquals(_vpc.cidr_block, '172.16.0.0/16')
        _connectionMock.create_vpc.assert_called_once_with(
            CidrBlock='172.23.0.0/16'
        )
        _connectionMock.create_tags.assert_called_once_with(
            Resources=[self.vpc_id_mock],
            Tags=[{
                'Key': 'Name',
                'Value': 'Treadmill-vpc'
            }]
        )
        _connectionMock.modify_vpc_attribute.assert_called_once_with(
            VpcId=self.vpc_id_mock,
            EnableDnsHostnames={
                'Value': True
            })

    @mock.patch('treadmill.infra.connection.Connection')
    def test_create_subnet(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.create_subnet = mock.Mock(return_value={
            'Subnet': {'SubnetId': self.subnet_id_mock}
        })

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.create_subnet()

        _connectionMock.create_subnet.assert_called_once_with(
            VpcId=self.vpc_id_mock,
            CidrBlock='172.23.0.0/24',
            AvailabilityZone='us-east-1a'
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_create_internet_gateway(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.create_internet_gateway = mock.Mock(return_value={
            'InternetGateway': {
                'InternetGatewayId': self.gateway_id_mock
            }
        })
        _connectionMock.attach_internet_gatway = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.create_internet_gateway()

        self.assertEquals(_vpc.gateway_ids, [self.gateway_id_mock])
        _connectionMock.create_internet_gateway.assert_called_once()
        _connectionMock.attach_internet_gateway.assert_called_once_with(
            InternetGatewayId=self.gateway_id_mock,
            VpcId=self.vpc_id_mock
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_create_route_table(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.create_route_table = mock.Mock(return_value={
            'RouteTable': {
                'RouteTableId': self.route_table_id_mock
            }
        })
        _connectionMock.create_route = mock.Mock(return_value={
            'Return': True
        })
        _connectionMock.associate_route_table = mock.Mock(return_value={
            'AssociationId': 'foobar'
        })

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.gateway_ids = [self.gateway_id_mock]
        _vpc.subnet_ids = [self.subnet_id_mock]
        _vpc.create_route_table()

        _connectionMock.create_route_table.assert_called_once_with(
            VpcId=self.vpc_id_mock
        )
        _connectionMock.create_route.assert_called_once_with(
            RouteTableId=self.route_table_id_mock,
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=self.gateway_id_mock
        )
        _connectionMock.associate_route_table.assert_called_once_with(
            SubnetId=self.subnet_id_mock,
            RouteTableId=self.route_table_id_mock
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_create_security_group(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.create_security_group = mock.Mock(return_value={
            'GroupId': self.security_group_id_mock
        })

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.create_security_group(
            GroupName='foobar',
            Description='foobar description'
        )

        self.assertEquals(_vpc.secgroup_ids, [self.security_group_id_mock])
        _connectionMock.create_security_group.assert_called_once_with(
            GroupName='foobar',
            Description='foobar description',
            VpcId=self.vpc_id_mock
        )

    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('time.time', mock.Mock(return_value=786.007))
    def test_create_hosted_zone(self, connectionMock):
        _connectionMock = connectionMock('route53')
        expected_hosted_zone = {
            'HostedZone': {
                'Id': 'Some-Zone-Id'
            },
            'VPC': {
                'Id': self.vpc_id_mock
            }
        }
        _connectionMock.create_hosted_zone = mock.Mock(
            return_value=expected_hosted_zone
        )

        _vpc = vpc.VPC(self.vpc_id_mock, domain='foo.bar')
        _vpc.create_hosted_zone()

        self.assertEquals(
            _vpc.hosted_zone_id,
            expected_hosted_zone['HostedZone']['Id']
        )
        _connectionMock.create_hosted_zone.assert_called_once_with(
            Name='foo.bar',
            VPC={
                'VPCRegion': 'us-east-1',
                'VPCId': self.vpc_id_mock,
            },
            HostedZoneConfig={
                'PrivateZone': True
            },
            CallerReference='786'
        )

    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('time.time', mock.Mock(return_value=786.007))
    def test_create_hosted_zone_reverse(self, connectionMock):
        _connectionMock = connectionMock('route53')
        expected_hosted_zone = {
            'HostedZone': {
                'Id': 'Some-Zone-Id'
            },
            'VPC': {
                'Id': self.vpc_id_mock
            }
        }
        _connectionMock.create_hosted_zone = mock.Mock(
            return_value=expected_hosted_zone
        )

        _vpc = vpc.VPC(self.vpc_id_mock, domain='foo.bar')
        _vpc.cidr_block = '172.10.0.0/16'
        _vpc.create_hosted_zone(Reverse=True)

        self.assertEquals(
            _vpc.reverse_hosted_zone_id,
            expected_hosted_zone['HostedZone']['Id']
        )
        _connectionMock.create_hosted_zone.assert_called_once_with(
            Name='10.172.in-addr.arpa',
            VPC={
                'VPCRegion': 'us-east-1',
                'VPCId': self.vpc_id_mock,
            },
            HostedZoneConfig={
                'PrivateZone': True
            },
            CallerReference='786'
        )

    @mock.patch('treadmill.infra.instances.Connection', mock.Mock())
    @mock.patch('treadmill.infra.instances.Instances')
    def test_get_instances(self, instances_mock):
        instance0_json = {'InstanceId': 'instance-id-0'}
        instance1_json = {'InstanceId': 'instance-id-1'}
        expected_instances = [
            Instance(
                id='instance-id-0',
                metadata=instance0_json
            ),
            Instance(
                id='instance-id-1',
                metadata=instance1_json
            )
        ]

        instances_mock.get = mock.Mock(
            return_value=Instances(instances=expected_instances)
        )

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.get_instances()

        self.assertEquals(
            _vpc.instances.instances,
            expected_instances
        )

        instances_mock.get.assert_called_once_with(
            filters=[{
                'Name': 'vpc-id',
                'Values': [self.vpc_id_mock]
            }]
        )

    @mock.patch('treadmill.infra.instances.Connection', mock.Mock())
    @mock.patch('treadmill.infra.instances.Instances')
    def test_terminate_instances(self, instances_mock):
        instances_obj_mock = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.instances = instances_obj_mock

        _vpc.terminate_instances()

        instances_obj_mock.terminate.assert_called_once()

    @mock.patch('treadmill.infra.connection.Connection')
    def test_get_security_group_ids(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.describe_security_groups = mock.Mock(return_value={
            'SecurityGroups': [{
                'GroupId': 'secgroup-id-0',
                'GroupName': 'foobar'
            }, {
                'GroupId': 'secgroup-id-1',
                'GroupName': 'default'
            }]
        })

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.get_security_group_ids()

        _connectionMock.describe_security_groups.assert_called_once_with(
            Filters=[{
                'Name': 'vpc-id',
                'Values': [self.vpc_id_mock]
            }]
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_delete_security_groups(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.delete_security_group = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.secgroup_ids = ['secgroup-id-0', 'secgroup-id-1']
        _vpc.delete_security_groups()

        self.assertCountEqual(
            _connectionMock.delete_security_group.mock_calls,
            [
                mock.mock.call(GroupId='secgroup-id-0'),
                mock.mock.call(GroupId='secgroup-id-1')
            ]
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_get_hosted_zone_ids(self, connectionMock):
        _connectionMock = connectionMock('route53')
        _connectionMock.list_hosted_zones = mock.Mock(return_value={
            'HostedZones': [{
                'Id': 'zone-id',
                'Name': 'zone-name',
            }, {
                'Id': 'zone-id-1',
                'Name': 'zone-name',
            }]
        })
        _connectionMock.get_hosted_zone = mock.Mock()
        _connectionMock.get_hosted_zone.side_effect = [
            {
                'HostedZone': {
                    'Id': 'zone-id',
                    'Name': 'zone-name',
                },
                'VPCs': [{
                    'VPCRegion': 'region',
                    'VPCId': self.vpc_id_mock
                }]
            },
            {
                'HostedZone': {
                    'Id': 'zone-id-1',
                    'Name': 'zone-name',
                },
                'VPCs': [{
                    'VPCRegion': 'region',
                    'VPCId': 'foobar'
                }]
            }

        ]

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.get_hosted_zone_ids()
        self.assertEquals(_vpc.hosted_zone_ids, ['zone-id'])

        _connectionMock.list_hosted_zones.assert_called_once()
        self.assertCountEqual(
            _connectionMock.get_hosted_zone.mock_calls,
            [
                mock.mock.call(Id='zone-id'),
                mock.mock.call(Id='zone-id-1')
            ]
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_delete_hosted_zones(self, connectionMock):
        _connectionMock = connectionMock('route53')
        _connectionMock.delete_hosted_zone = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.hosted_zone_ids = [1]

        _vpc.delete_hosted_zones()

        _connectionMock.delete_hosted_zone.assert_called_once_with(
            Id=1
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_get_route_related_ids(self, connectionMock):
        route_table_response_mock = {
            'RouteTables': [{
                'RouteTableId': 'route_table_id_0',
                'VpcId': self.vpc_id_mock,
                'Routes': [{
                    'GatewayId': 'gateway_id_0',
                    'InstanceId': 'route_instance_id_0',
                }],
                'Associations': [{
                    'RouteTableAssociationId': 'ass_id_0',
                    'RouteTableId': 'route_table_id_0',
                    'SubnetId': 'subnet_id_0',
                }]
            }, {
                'RouteTableId': 'route_table_id_1',
                'VpcId': self.vpc_id_mock,
                'Routes': [{
                    'GatewayId': 'gateway_id_1',
                    'InstanceId': 'route_instance_id_1',
                }],
                'Associations': [{
                    'RouteTableAssociationId': 'ass_id_1',
                    'RouteTableId': 'route_table_id_1',
                    'SubnetId': 'subnet_id_1',
                }]
            }]
        }

        _connectionMock = connectionMock()
        _connectionMock.describe_route_tables = mock.Mock(
            return_value=route_table_response_mock
        )
        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.get_route_related_ids()
        self.assertEquals(_vpc.association_ids, ['ass_id_0', 'ass_id_1'])
        self.assertEquals(_vpc.route_table_ids,
                          ['route_table_id_0', 'route_table_id_1'])
        self.assertEquals(_vpc.subnet_ids, ['subnet_id_0', 'subnet_id_1'])

        _connectionMock.describe_route_tables.assert_called_once_with(
            Filters=[{
                'Name': 'vpc-id',
                'Values': [self.vpc_id_mock]
            }]
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_delete_route_tables(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.disassociate_route_table = mock.Mock()
        _connectionMock.delete_route_table = mock.Mock()
        _connectionMock.delete_subnet = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.route_related_ids = 'foo'
        _vpc.association_ids = ['ass-id']
        _vpc.route_table_ids = ['route-table-id']
        _vpc.subnet_ids = ['subnet-id']
        _vpc.delete_route_tables()

        _connectionMock.disassociate_route_table.assert_called_once_with(
            AssociationId='ass-id'
        )

        _connectionMock.delete_route_table.assert_called_once_with(
            RouteTableId='route-table-id'
        )

        _connectionMock.delete_subnet.assert_called_once_with(
            SubnetId='subnet-id'
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_delete(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.delete_vpc = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.delete()

        _connectionMock.delete_vpc.assert_called_once_with(
            VpcId=self.vpc_id_mock
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_get_internet_gateway_id(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.describe_internet_gateways = mock.Mock(return_value={
            'InternetGateways': [
                {
                    'InternetGatewayId': self.internet_gateway_id_mock
                }
            ]
        })

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.get_internet_gateway_ids()

        self.assertEquals(_vpc.gateway_ids, [self.internet_gateway_id_mock])

        _connectionMock.describe_internet_gateways.assert_called_once_with(
            Filters=[{
                'Name': 'attachment.vpc-id',
                'Values': [self.vpc_id_mock]
            }]
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_delete_internet_gateway(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.delete_internet_gateway = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.gateway_ids = [self.internet_gateway_id_mock]
        _vpc.delete_internet_gateway()

        _connectionMock.delete_internet_gateway.assert_called_once_with(
            InternetGatewayId=self.internet_gateway_id_mock
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_associate_dhcp_options(self, connectionMock):
        _connectionMock = connectionMock()
        _connectionMock.create_dhcp_options = mock.Mock(return_value={
            'DhcpOptions': {
                'DhcpOptionsId': 'some-dhcp-id'
            }
        })
        _connectionMock.associate_dhcp_options = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock, domain='cloud.ms.com')
        _vpc.associate_dhcp_options()

        _connectionMock.create_dhcp_options.assert_called_once_with(
            DhcpConfigurations=[
                {
                    'Key': 'domain-name',
                    'Values': ['cloud.ms.com']
                },
                {
                    'Key': 'domain-name-servers',
                    'Values': ['AmazonProvidedDNS']
                }
            ]
        )
        _connectionMock.associate_dhcp_options.assert_called_once_with(
            DhcpOptionsId='some-dhcp-id',
            VpcId=self.vpc_id_mock
        )


if __name__ == '__main__':
    unittest.main()
