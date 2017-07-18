"""
Unit test for EC2 ldap.
"""

import unittest
import mock

from treadmill.infra.setup.ldap import LDAP


class LDAPTest(unittest.TestCase):
    """Tests EC2 LDAP"""

    @mock.patch('treadmill.infra.configuration.LDAP')
    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('treadmill.infra.vpc.VPC')
    @mock.patch('treadmill.infra.instances.Instances')
    def test_setup_ldap(self, InstancesMock, VPCMock,
                        ConnectionMock, LDAPConfigurationMock):
        instance_mock = mock.Mock(private_ip='1.1.1.1')
        instances_mock = mock.Mock(instances=[instance_mock])
        InstancesMock.create = mock.Mock(return_value=instances_mock)
        _vpc_id_mock = 'vpc-id'
        _vpc_mock = VPCMock(id=_vpc_id_mock,
                            domain='foo.bar')
        _vpc_mock.hosted_zone_id = 'hosted-zone-id'
        _vpc_mock.reverse_hosted_zone_id = 'reverse-hosted-zone-id'
        _vpc_mock.gateway_ids = [123]
        _vpc_mock.secgroup_ids = ['secgroup-id']
        _vpc_mock.subnets = [mock.Mock(id='subnet-id')]
        _ldap_configuration_mock = LDAPConfigurationMock()
        _ldap_configuration_mock.get_userdata = mock.Mock(
            return_value='user-data-script'
        )
        ldap = LDAP(
            name='ldap',
            domain='foo.bar',
            vpc_id=_vpc_id_mock,
        )
        ldap.setup(
            image_id='foo-123',
            count=1,
            cidr_block='cidr-block',
            key='some-key',
            instance_type='small',
            tm_release='release',
            app_root='app-root',
            ldap_hostname='hostname'
        )

        self.assertEqual(ldap.subnet.instances, instances_mock)
        InstancesMock.create.assert_called_once_with(
            image_id='foo-123',
            name='ldap',
            count=1,
            subnet_id='subnet-id',
            instance_type='small',
            secgroup_ids=['secgroup-id'],
            key_name='some-key',
            hosted_zone_id='hosted-zone-id',
            reverse_hosted_zone_id='reverse-hosted-zone-id',
            user_data='user-data-script',
            domain='foo.bar',
            role='LDAP'
        )
        _vpc_mock.load_hosted_zone_ids.assert_called_once()
        _vpc_mock.load_security_group_ids.assert_called_once()
        _vpc_mock.create_subnet.assert_called_once_with(
            cidr_block='cidr-block',
            name='ldap',
            gateway_id=123
        )

        self.assertEqual(
            LDAPConfigurationMock.mock_calls[1],
            mock.mock.call(
                domain='foo.bar',
                ldap_hostname='hostname',
                tm_release='release',
                subnet_id=None,
                name='ldap',
                app_root='app-root'
            )
        )
        _ldap_configuration_mock.get_userdata.assert_called_once()

    @mock.patch('treadmill.infra.subnet.Subnet')
    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('treadmill.infra.vpc.VPC')
    def test_ldap_destroy(self, VPCMock, ConnectionMock,
                          SubnetMock):
        _subnet_mock = SubnetMock(id='subnet-id')
        _subnet_mock.instances = mock.Mock(instances=[
            mock.Mock(private_ip='1.1.1.1')
        ])
        vpc_mock = VPCMock(
            id='vpc-id',
            domain='foo.bar',
        )
        vpc_mock.load_hosted_zone_ids = mock.Mock()
        vpc_mock.hosted_zone_id = 'hosted-zone-id'
        vpc_mock.reverse_hosted_zone_id = 'reverse-hosted-zone-id'
        ldap = LDAP(
            vpc_id='vpc-id',
            domain='foo.bar',
            name='ldap'
        )
        ldap.destroy(
            subnet_id='subnet-id'
        )
        _subnet_mock.destroy.assert_called_once_with(
            hosted_zone_id='hosted-zone-id',
            reverse_hosted_zone_id='reverse-hosted-zone-id',
            domain='foo.bar',
            role='LDAP'
        )
        vpc_mock.load_hosted_zone_ids.assert_called_once()
