"""
Unit test for VPC.
"""

import unittest
import mock

from treadmill.infra import vpc


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
            return_value={'Vpc': {'VpcId': self.vpc_id_mock}}
        )
        _connectionMock.create_tags = mock.Mock()

        _vpc = vpc.VPC()
        _vpc.create()

        self.assertEquals(_vpc.id, self.vpc_id_mock)
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

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.create_hosted_zone()

        self.assertEquals(
            _vpc.hosted_zone_id,
            expected_hosted_zone['HostedZone']['Id']
        )
        _connectionMock.create_hosted_zone.assert_called_once_with(
            Name='tw.treadmill',
            VPC={
                'VPCRegion': 'us-east-1',
                'VPCId': self.vpc_id_mock,
            },
            HostedZoneConfig={
                'PrivateZone': True
            },
            CallerReference='786'
        )

    @mock.patch('treadmill.infra.instance.Connection', mock.Mock())
    @mock.patch('treadmill.infra.instance.Instance')
    def test_get_instances(self, instance_mock):
        expected_instances = [
            {
                'InstanceId': 'instance-id-0',
            },
            {
                'InstanceId': 'instance-id-1'
            }
        ]

        instance_mock.load_json = mock.Mock(
            return_value=expected_instances
        )

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.get_instances()

        self.assertEquals(
            _vpc.instance_ids,
            ['instance-id-0', 'instance-id-1']
        )

        self.assertEquals(_vpc.instances, expected_instances)
        instance_mock.load_json.assert_called_once_with(
            ids=[],
            filters=[{
                'Name': 'vpc-id',
                'Values': [self.vpc_id_mock]
            }]
        )

    @mock.patch('treadmill.infra.instance.Connection', mock.Mock())
    @mock.patch('treadmill.infra.instance.Instance')
    def test_terminate_instances(self, instance_mock):
        instance_obj_mock = mock.Mock()
        instance_mock.return_value = instance_obj_mock

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.instance_ids = ['instance-id-0', 'instance-id-1']
        _vpc.volume_ids = [1, 2]
        _vpc.terminate_instances()

        instance_mock.assert_called_once_with(
            ids=['instance-id-0', 'instance-id-1']
        )
        instance_obj_mock.terminate.assert_called_once()

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
    def test_get_hosted_zone_id(self, connectionMock):
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
        _connectionMock.get_hosted_zone = mock.Mock(return_value={
            'HostedZone': {
                'Id': 'zone-id',
                'Name': 'zone-name',
            },
            'VPCs': [{
                'VPCRegion': 'region',
                'VPCId': self.vpc_id_mock
            }]
        })

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.get_hosted_zone_id()

        _connectionMock.list_hosted_zones.assert_called_once()
        _connectionMock.get_hosted_zone.assert_called_once_with(Id='zone-id')
        self.assertEquals(_vpc.hosted_zone_id, 'zone-id')

    @mock.patch('treadmill.infra.connection.Connection')
    def test_delete_hosted_zone(self, connectionMock):
        _connectionMock = connectionMock('route53')
        _connectionMock.delete_hosted_zone = mock.Mock()

        _vpc = vpc.VPC(self.vpc_id_mock)
        _vpc.hosted_zone_id = 1

        _vpc.delete_hosted_zone()

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


if __name__ == '__main__':
    unittest.main()
