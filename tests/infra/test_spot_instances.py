"""
Unit test for EC2 spot instance.
"""

import unittest
import mock

from treadmill.infra.spot_instances import SpotInstances


class SpotInstancesTest(unittest.TestCase):
    """Tests EC2 instance"""

    @mock.patch('treadmill.infra.instances.connection.Connection')
    def test_create(self, ConnectionMock):
        ConnectionMock.context.domain = 'joo.goo'
        ConnectionMock.context.region_name = 'ca-central-1'
        instance1_metadata_mock = {
            'InstanceId': 1,
            'AmiLaunchIndex': 0
        }
        instance2_metadata_mock = {
            'InstanceId': 2,
            'AmiLaunchIndex': 599
        }
        sample_spot_requests = [
            {'State': 'active', 'SpotRequestId': '1', 'InstanceId': '1'},
            {'State': 'active', 'SpotRequestId': '2', 'InstanceId': '2'},
        ]

        conn_mock = ConnectionMock()
        conn_mock.request_spot_instances = mock.Mock(return_value={
            'SpotInstanceRequests': sample_spot_requests
        })
        conn_mock.describe_instances = mock.Mock(side_effect=[
            {
                'Reservations': [{'Instances': [instance1_metadata_mock]}]
            },
            {
                'Reservations': [{'Instances': [instance2_metadata_mock]}]
            }
        ])
        conn_mock.create_tags = mock.Mock()
        conn_mock.describe_images = mock.Mock(return_value={
            'Images': [{'ImageId': 'ami-123'}]
        })

        SpotInstances.create(
            key_name='key',
            name='foo',
            image='foo-123',
            count=2,
            instance_type='m4.large',
            subnet_id='',
            secgroup_ids=None,
            user_data='',
            role='role'
        )

        conn_mock.request_spot_instances.assert_called_with(
            LaunchSpecification={
                'ImageId': 'ami-123',
                'InstanceType': 'm4.large',
                'KeyName': 'key',
                'NetworkInterfaces': [{
                    'DeviceIndex': 0,
                    'SubnetId': '',
                    'Groups': None,
                    'AssociatePublicIpAddress': True
                }],
                'UserData': ''
            },
            SpotPrice='0.111',
            InstanceCount=2
        )
        conn_mock.describe_instances.assert_has_calls(
            [mock.call(InstanceIds=['1']), mock.call(InstanceIds=['2'])]
        )
