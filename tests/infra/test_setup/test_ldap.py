"""
Unit test for EC2 ldap.
"""

import unittest
import mock

from treadmill.infra.setup.ldap import LDAP


class LDAPTest(unittest.TestCase):
    """Tests EC2 LDAP"""

    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('treadmill.infra.vpc.VPC')
    @mock.patch('treadmill.infra.instances.Instances')
    def test_setup_ldap(self, InstancesMock, VPCMock, ConnectionMock):
        instance_mock = mock.Mock(private_ip='1.1.1.1')
        instances_mock = mock.Mock(instances=[instance_mock])
        InstancesMock.create = mock.Mock(return_value=instances_mock)
        _vpc_id_mock = 'vpc-id'
        _vpc_mock = VPCMock(id=_vpc_id_mock,
                            region_name='region',
                            domain='foo.bar')
        _vpc_mock.hosted_zone_id = 'hosted-zone-id'
        _vpc_mock.reverse_hosted_zone_id = 'reverse-hosted-zone-id'
        _vpc_mock.subnet_ids = [123]
        ldap = LDAP(
            name='ldap',
            domain='foo.bar',
            vpc_id=_vpc_id_mock,
            region_name='region'
        )
        ldap.setup(
            image_id='foo-123',
            count=1,
            cidr_block='cidr-block'
        )

        self.assertEqual(ldap.instances, instances_mock)
        InstancesMock.create.assert_called_once_with(
            image_id='foo-123',
            name='ldap',
            count=1,
            subnet_id=123,
            instance_type='t2.medium'
        )
        _vpc_mock.get_hosted_zone_ids.assert_called_once()
        _vpc_mock.create_subnet.assert_called_once_with(
            'region', 'cidr-block'
        )

        self.assertCountEqual(
            instance_mock.upsert_dns_record.mock_calls,
            [
                mock.mock.call('hosted-zone-id',
                               'foo.bar'),
                mock.mock.call('reverse-hosted-zone-id',
                               'foo.bar',
                               reverse=True)
            ]
        )

    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('treadmill.infra.vpc.VPC')
    @mock.patch('treadmill.infra.instances.Instances')
    def test_ldap_destroy(self, InstancesMock, VPCMock, ConnectionMock):
        instance_mock = mock.Mock(private_ip='1.1.1.1')
        instances_mock = mock.Mock(instances=[instance_mock])
        InstancesMock.get = mock.Mock(return_value=instances_mock)
        vpc_mock = VPCMock(
            id='vpc-id',
            domain='foo.bar',
            region_name='region'
        )
        vpc_mock.get_hosted_zone_ids = mock.Mock()
        vpc_mock.hosted_zone_id = 'hosted-zone-id'
        vpc_mock.reverse_hosted_zone_id = 'reverse-hosted-zone-id'
        ldap = LDAP(
            vpc_id='vpc-id',
            domain='foo.bar',
            region_name='region',
            name='ldap'
        )
        ldap.instances = InstancesMock()
        ldap.destroy(
            instance_id='instance-id',
        )

        InstancesMock.get.assert_called_once_with(ids=['instance-id'])
        vpc_mock.get_hosted_zone_ids.assert_called_once()
        ldap.instances.terminate.assert_called_once_with(
            hosted_zone_id='hosted-zone-id',
            reverse_hosted_zone_id='reverse-hosted-zone-id',
            domain='foo.bar'
        )
