"""
Unit test for EC2 instance.
"""

import unittest
import mock

from treadmill.infra.instance import Instance


class InstanceTest(unittest.TestCase):
    """Tests ec2 instance creation."""

    @mock.patch('treadmill.infra.instance.Connection')
    def test_create_instance(self, ConnectionMock):
        conn_mock = ConnectionMock()
        conn_mock.run_instances = mock.Mock(
            return_value={
                'Instances': [
                    {
                        'InstanceId': 1
                    },
                    {
                        'InstanceId': 2
                    }
                ]
            }
        )
        conn_mock.create_tags = mock.Mock()

        master = Instance(Name='foo', ImageId='foo-123', Count=2)
        master.create()

        self.assertEquals(master.ids, [1, 2])

        conn_mock.run_instances.assert_called_with(
            ImageId='foo-123',
            InstanceType='t2.small',
            MaxCount=2,
            MinCount=2,
            SecurityGroupIds=None,
            SubnetId='',
        )
        self.assertCountEqual(
            conn_mock.create_tags.mock_calls,
            [
                mock.mock.call(
                    Resources=[1],
                    Tags=[{
                        'Key': 'Name',
                        'Value': 'foo1'
                    }]
                ),
                mock.mock.call(
                    Resources=[2],
                    Tags=[{
                        'Key': 'Name',
                        'Value': 'foo2'
                    }]
                )

            ]
        )

    @mock.patch('treadmill.infra.instance.Connection')
    def test_terminate(self, ConnectionMock):
        conn_mock = ConnectionMock()

        instance = Instance(Name='foo', ImageId='foo-123')
        instance.ids = [1, 2]
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

    @mock.patch('treadmill.infra.instance.Connection')
    def test_get_volume_ids(self, connectionMock):
        conn_mock = connectionMock()
        conn_mock.describe_volumes = mock.Mock(return_value={
            'Volumes': [{
                'VolumeId': 'vol-id'
            }]
        })

        instance = Instance(ids=[1])
        instance.get_volume_ids()

        self.assertEquals(instance.volume_ids, ['vol-id'])

    @mock.patch('treadmill.infra.instance.Connection')
    def test_load_json_with_instance_ids(self, ConnectionMock):
        conn_mock = ConnectionMock()

        sample_instances = [
            {'InstanceId': 1}, {'InstanceId': 2}, {'InstanceId': 3}
        ]
        conn_mock.describe_instances = mock.Mock(return_value={
            'Reservations': [{'Instances': sample_instances}]
        })

        instance_details = Instance.load_json([1, 2, 3])

        conn_mock.describe_instances.assert_called_once_with(
            InstanceIds=[1, 2, 3]
        )
        self.assertEquals(instance_details, sample_instances)

    @mock.patch('treadmill.infra.instance.Connection')
    def test_load_json_with_filters(self, ConnectionMock):
        conn_mock = ConnectionMock()

        sample_instances = [
            {'InstanceId': 1}, {'InstanceId': 2}, {'InstanceId': 3}
        ]
        conn_mock.describe_instances = mock.Mock(return_value={
            'Reservations': [{'Instances': sample_instances}]
        })

        instance_details = Instance.load_json(filters=[{'foo': 'bar'}])

        conn_mock.describe_instances.assert_called_once_with(
            Filters=[{'foo': 'bar'}]
        )
        self.assertEquals(instance_details, sample_instances)


if __name__ == '__main__':
    unittest.main()
