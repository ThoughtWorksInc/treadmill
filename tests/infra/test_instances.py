"""
Unit test for EC2 instance.
"""

import unittest
import mock

from treadmill.infra.instances import Instance
from treadmill.infra.instances import Instances


class InstanceTest(unittest.TestCase):
    """Tests EC2 instance"""

    @mock.patch('treadmill.infra.instances.Connection')
    def test_create_tags(self, ConnectionMock):
        conn_mock = ConnectionMock()
        conn_mock.create_tags = mock.Mock()

        instance = Instance(
            Name='foo',
            id='1',
            metadata={'AmiLaunchIndex': 100}
        )
        instance.create_tags()

        conn_mock.create_tags.assert_called_once_with(
            Resources=['1'],
            Tags=[{
                'Key': 'Name',
                'Value': 'foo101'
            }]
        )


class InstancesTest(unittest.TestCase):
    """Tests instances collection"""

    @mock.patch('treadmill.infra.instances.Connection')
    def test_create(self, ConnectionMock):
        instance1_metadata_mock = {
            'InstanceId': 1,
            'AmiLaunchIndex': 999
        }
        instance2_metadata_mock = {
            'InstanceId': 2,
            'AmiLaunchIndex': 599
        }
        sample_instances = [
            {'InstanceId': 1},
            {'InstanceId': 2},
        ]
        instances_mock = [
            instance1_metadata_mock,
            instance2_metadata_mock
        ]

        conn_mock = ConnectionMock()
        conn_mock.run_instances = mock.Mock(return_value={
            'Instances': sample_instances
        })
        conn_mock.describe_instances = mock.Mock(return_value={
            'Reservations': [{'Instances': instances_mock}]
        })
        conn_mock.create_tags = mock.Mock()

        instances = Instances.create(
            Name='foo',
            ImageId='foo-123',
            Count=2
        ).instances

        instance_ids = [i.id for i in instances]

        self.assertEquals(len(instances), 2)
        self.assertIsInstance(instances[0], Instance)
        self.assertIsInstance(instances[1], Instance)
        self.assertCountEqual(instance_ids, [1, 2])
        self.assertEquals(instances[0].metadata, instance1_metadata_mock)
        self.assertEquals(instances[1].metadata, instance2_metadata_mock)

        conn_mock.run_instances.assert_called_with(
            ImageId='foo-123',
            InstanceType='t2.small',
            KeyName='ms_treadmill_dev',
            MaxCount=2,
            MinCount=2,
            SecurityGroupIds=None,
            SubnetId='',
            UserData='',
        )
        conn_mock.describe_instances.assert_called_with(
            InstanceIds=[1, 2]
        )
        self.assertCountEqual(
            conn_mock.create_tags.mock_calls,
            [
                mock.mock.call(
                    Resources=[1],
                    Tags=[{
                        'Key': 'Name',
                        'Value': 'foo1000'
                    }]
                ),
                mock.mock.call(
                    Resources=[2],
                    Tags=[{
                        'Key': 'Name',
                        'Value': 'foo600'
                    }]
                )

            ]
        )

    @mock.patch('treadmill.infra.instances.Connection')
    def test_terminate(self, ConnectionMock):
        conn_mock = ConnectionMock()

        instance = Instances(instances=[Instance(id=1), Instance(id=2)])
        instance.volume_ids = ['vol-id0', 'vol-id1']

        instance.terminate()

        conn_mock.describe_instance_status.assert_called()
        conn_mock.terminate_instances.assert_called_once_with(
            InstanceIds=[1, 2]
        )
        self.assertCountEqual(
            conn_mock.delete_volume.mock_calls,
            [
                mock.mock.call(VolumeId='vol-id0'),
                mock.mock.call(VolumeId='vol-id1')
            ]
        )

    @mock.patch('treadmill.infra.instances.Connection')
    def test_get_volume_ids(self, connectionMock):
        conn_mock = connectionMock()
        conn_mock.describe_volumes = mock.Mock(return_value={
            'Volumes': [{
                'VolumeId': 'vol-id'
            }]
        })

        instance = Instances([Instance(id=1)])
        instance.get_volume_ids()

        self.assertEquals(instance.volume_ids, ['vol-id'])
        conn_mock.describe_volumes.assert_called_once_with(
            Filters=[{
                'Name': 'attachment.instance-id',
                'Values': [1]
            }]
        )

    @mock.patch('treadmill.infra.instances.Connection')
    def test_load_json_with_instance_ids(self, ConnectionMock):
        conn_mock = ConnectionMock()

        sample_instances = [
            {'InstanceId': 1}, {'InstanceId': 2}, {'InstanceId': 3}
        ]
        conn_mock.describe_instances = mock.Mock(return_value={
            'Reservations': [{'Instances': sample_instances}]
        })

        instance_details = Instances.load_json([1, 2, 3])

        conn_mock.describe_instances.assert_called_once_with(
            InstanceIds=[1, 2, 3]
        )
        self.assertEquals(instance_details, sample_instances)

    @mock.patch('treadmill.infra.instances.Connection')
    def test_load_json_with_filters(self, ConnectionMock):
        conn_mock = ConnectionMock()

        sample_instances = [
            {'InstanceId': 1}, {'InstanceId': 2}, {'InstanceId': 3}
        ]
        conn_mock.describe_instances = mock.Mock(return_value={
            'Reservations': [{'Instances': sample_instances}]
        })

        instance_details = Instances.load_json(filters=[{'foo': 'bar'}])

        conn_mock.describe_instances.assert_called_once_with(
            Filters=[{'foo': 'bar'}]
        )
        self.assertEquals(instance_details, sample_instances)


if __name__ == '__main__':
    unittest.main()
