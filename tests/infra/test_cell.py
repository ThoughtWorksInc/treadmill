"""
Unit test for EC2 cell.
"""

import unittest
import mock

from treadmill.infra.cell import Cell


class CellTest(unittest.TestCase):

    @mock.patch('treadmill.infra.connection.Connection')
    def test_init(self, ConnectionMock):
        conn_mock = ConnectionMock()
        cell = Cell(
            id=1,
            vpc_id='vpc-id',
            metadata={
                'Tags': [{
                    'Key': 'Name',
                    'Value': 'goo'
                }]
            }
        )

        self.assertEquals(cell.vpc_id, 'vpc-id')
        self.assertEquals(cell.name, 'goo')
        self.assertEquals(cell.ec2_conn, conn_mock)

    @mock.patch('treadmill.infra.connection.Connection')
    def test_create_tags(self, ConnectionMock):
        conn_mock = ConnectionMock()
        conn_mock.create_tags = mock.Mock()

        cell = Cell(
            name='foo',
            id='1',
            vpc_id='vpc-id'
        )
        cell.create_tags()

        conn_mock.create_tags.assert_called_once_with(
            Resources=['1'],
            Tags=[{
                'Key': 'Name',
                'Value': 'foo'
            }]
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_create(self, ConnectionMock):
        ConnectionMock.region_name = 'us-east-1'
        conn_mock = ConnectionMock()
        cell_json_mock = {
            'Subnet': {
                'SubnetId': '1'
            }
        }
        conn_mock.create_subnet = mock.Mock(return_value=cell_json_mock)
        conn_mock.create_route_table = mock.Mock(return_value={
            'RouteTable': {'RouteTableId': 'route-table-id'}
        })

        _cell = Cell.create(
            cidr_block='172.23.0.0/24',
            vpc_id='vpc-id',
            name='foo',
            gateway_id='gateway-id'
        )
        self.assertEqual(_cell.id, '1')
        self.assertEqual(_cell.name, 'foo')
        self.assertEqual(_cell.metadata, cell_json_mock)
        conn_mock.create_subnet.assert_called_once_with(
            VpcId='vpc-id',
            CidrBlock='172.23.0.0/24',
            AvailabilityZone='us-east-1a'
        )
        conn_mock.create_tags.assert_called_once_with(
            Resources=['1'],
            Tags=[{
                'Key': 'Name',
                'Value': 'foo'
            }]
        )
        conn_mock.create_route_table.assert_called_once_with(
            VpcId='vpc-id'
        )
        conn_mock.create_route.assert_called_once_with(
            RouteTableId='route-table-id',
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId='gateway-id'
        )
        conn_mock.associate_route_table.assert_called_once_with(
            RouteTableId='route-table-id',
            SubnetId='1',
        )


if __name__ == '__main__':
    unittest.main()
