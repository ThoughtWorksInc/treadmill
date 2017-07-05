"""
Unit test for EC2 subnet.
"""

import unittest
import mock

from treadmill.infra.subnet import Subnet


class SubnetTest(unittest.TestCase):

    @mock.patch('treadmill.infra.connection.Connection')
    def test_init(self, ConnectionMock):
        conn_mock = ConnectionMock()
        subnet = Subnet(
            id=1,
            vpc_id='vpc-id',
            metadata={
                'Tags': [{
                    'Key': 'Name',
                    'Value': 'goo'
                }]
            }
        )

        self.assertEquals(subnet.vpc_id, 'vpc-id')
        self.assertEquals(subnet.name, 'goo')
        self.assertEquals(subnet.ec2_conn, conn_mock)

    @mock.patch('treadmill.infra.connection.Connection')
    def test_create_tags(self, ConnectionMock):
        conn_mock = ConnectionMock()
        conn_mock.create_tags = mock.Mock()

        subnet = Subnet(
            name='foo',
            id='1',
            vpc_id='vpc-id'
        )
        subnet.create_tags()

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
        subnet_json_mock = {
            'Subnet': {
                'SubnetId': '1'
            }
        }
        conn_mock.create_subnet = mock.Mock(return_value=subnet_json_mock)

        _subnet = Subnet.create(
            cidr_block='172.23.0.0/24',
            vpc_id='vpc-id',
            name='foo'
        )
        self.assertEqual(_subnet.id, '1')
        self.assertEqual(_subnet.name, 'foo')
        self.assertEqual(_subnet.metadata, subnet_json_mock)
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


if __name__ == '__main__':
    unittest.main()
