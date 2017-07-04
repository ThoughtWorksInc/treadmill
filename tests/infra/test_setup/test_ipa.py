"""
Unit test for EC2 ipa.
"""

import unittest
import mock

from treadmill.infra.setup.ipa import IPA


class IPATest(unittest.TestCase):
    """Tests EC2 ipa setup."""

    @mock.patch('treadmill.infra.setup.ipa.connection.Connection')
    @mock.patch('treadmill.infra.setup.ipa.vpc.VPC')
    @mock.patch('treadmill.infra.setup.ipa.instances.Instances')
    def test_setup_ipa(self, InstancesMock, VPCMock, ConnectionMock):
        instance_mock = mock.Mock(private_ip='1.1.1.1')
        instances_mock = mock.Mock(instances=[instance_mock])
        InstancesMock.create = mock.Mock(return_value=instances_mock)
        conn_mock = ConnectionMock('route53')
        _vpc_id_mock = 'vpc-id'
        _vpc_mock = VPCMock(id=_vpc_id_mock,
                            region_name='region',
                            domain='foo.bar')
        _vpc_mock.hosted_zone_id = 'hosted-zone-id'
        _vpc_mock.reverse_hosted_zone_id = 'reverse-hosted-zone-id'
        _vpc_mock.subnet_ids = [123]
        ipa = IPA(
            name='ipa',
            domain='foo.bar',
            vpc_id=_vpc_id_mock,
            region_name='region'
        )
        ipa.setup(
            image_id='foo-123',
            count=1,
            cidr_block='cidr-block'
        )

        self.assertEqual(ipa.instances, instances_mock)
        InstancesMock.create.assert_called_once_with(
            image_id='foo-123',
            name='ipa',
            count=1,
            subnet_id=123,
            instance_type='t2.medium'
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
        _vpc_mock.get_hosted_zone_ids.assert_called_once()
        _vpc_mock.create_subnet.assert_called_once_with(
            'region', 'cidr-block'
        )

        expected_calls = [
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_kerberos-master._tcp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 88 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_kerberos-master._udp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 88 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_kerberos._tcp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 88 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_kerberos._udp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 88 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_kpasswd._tcp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 464 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_kpasswd._udp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 464 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_ldap._tcp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 389 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_ntp._udp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 123 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': 'ipa-ca.foo.bar.',
                            'Type': 'A',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '1.1.1.1'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': '_kerberos.foo.bar.',
                            'Type': 'TXT',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '"FOO.BAR"'
                            }]
                        }
                    }]
                }
            )
        ]
        self.assertCountEqual(
            conn_mock.change_resource_record_sets.mock_calls,
            expected_calls
        )

    @mock.patch('treadmill.infra.setup.ipa.connection.Connection')
    @mock.patch('treadmill.infra.setup.ipa.vpc.VPC')
    @mock.patch('treadmill.infra.setup.ipa.instances.Instances')
    def test_ipa_destroy(self, InstancesMock, VPCMock, ConnectionMock):
        instance_mock = mock.Mock(private_ip='1.1.1.1')
        instances_mock = mock.Mock(instances=[instance_mock])
        InstancesMock.get = mock.Mock(return_value=instances_mock)
        conn_mock = ConnectionMock('route53')
        vpc_mock = VPCMock(
            id='vpc-id',
            domain='foo.bar',
            region_name='region'
        )
        vpc_mock.get_hosted_zone_ids = mock.Mock()
        vpc_mock.hosted_zone_id = 'hosted-zone-id'
        vpc_mock.reverse_hosted_zone_id = 'reverse-hosted-zone-id'
        ipa = IPA(
            vpc_id='vpc-id',
            domain='foo.bar',
            region_name='region',
            name='ipa'
        )
        ipa.instances = InstancesMock()
        ipa.destroy(
            instance_id='instance-id',
        )

        InstancesMock.get.assert_called_once_with(ids=['instance-id'])
        vpc_mock.get_hosted_zone_ids.assert_called_once()
        ipa.instances.terminate.assert_called_once_with(
            hosted_zone_id='hosted-zone-id',
            reverse_hosted_zone_id='reverse-hosted-zone-id',
            domain='foo.bar'
        )
        expected_calls = [
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_kerberos-master._tcp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 88 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_kerberos-master._udp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 88 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_kerberos._tcp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 88 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_kerberos._udp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 88 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_kpasswd._tcp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 464 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_kpasswd._udp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 464 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_ldap._tcp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 389 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_ntp._udp.foo.bar.',
                            'Type': 'SRV',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '0 100 123 ipa.foo.bar.'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': 'ipa-ca.foo.bar.',
                            'Type': 'A',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '1.1.1.1'
                            }]
                        }
                    }]
                }
            ),
            mock.mock.call(
                HostedZoneId='hosted-zone-id',
                ChangeBatch={
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': '_kerberos.foo.bar.',
                            'Type': 'TXT',
                            'TTL': 86400,
                            'ResourceRecords': [{
                                'Value': '"FOO.BAR"'
                            }]
                        }
                    }]
                }
            )
        ]
        self.assertCountEqual(
            conn_mock.change_resource_record_sets.mock_calls,
            expected_calls
        )
