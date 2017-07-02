"""
Unit test for EC2 freeipa setup.
"""

import unittest
import mock

from treadmill.infra.setup.freeipa import FreeIPA


class FreeIPATest(unittest.TestCase):
    """Tests EC2 freeipa setup."""

    @mock.patch('treadmill.infra.setup.freeipa.connection.Connection')
    @mock.patch('treadmill.infra.setup.freeipa.vpc.VPC')
    @mock.patch('treadmill.infra.setup.freeipa.instances.Instances')
    def test_setup_freeipa(self, InstancesMock, VPCMock, ConnectionMock):
        instance_mock = mock.Mock(private_ip='1.1.1.1')
        instances_mock = mock.Mock(instances=[instance_mock])
        InstancesMock.create = mock.Mock(return_value=instances_mock)
        conn_mock = ConnectionMock('route53')
        _vpc_id_mock = 'vpc-id'
        _vpc_mock = VPCMock(_vpc_id_mock)
        _vpc_mock.hosted_zone_id = 'hosted-zone-id'
        freeipa = FreeIPA()
        freeipa.setup(
            name='freeipa',
            image_id='foo-123',
            count=1,
            subnet_id=123,
            domain='foo.bar',
            vpc_id=_vpc_id_mock
        )

        self.assertEqual(freeipa.instances, instances_mock)
        InstancesMock.create.assert_called_once_with(
            image_id='foo-123',
            name='freeipa',
            count=1,
            subnet_id=123,
            instance_type='t2.medium'
        )
        _vpc_mock.get_hosted_zone_ids.assert_called_once()
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
                                'Value': '0 100 88 freeipa.foo.bar.'
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
                                'Value': '0 100 88 freeipa.foo.bar.'
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
                                'Value': '0 100 88 freeipa.foo.bar.'
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
                                'Value': '0 100 88 freeipa.foo.bar.'
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
                                'Value': '0 100 464 freeipa.foo.bar.'
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
                                'Value': '0 100 464 freeipa.foo.bar.'
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
                                'Value': '0 100 389 freeipa.foo.bar.'
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
                                'Value': '0 100 123 freeipa.foo.bar.'
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

    @mock.patch('treadmill.infra.setup.freeipa.instances.Instances')
    def test_freeipa_destroy(self, InstancesMock):
        freeipa = FreeIPA()
        freeipa.instances = InstancesMock()
        freeipa.destroy()

        freeipa.instances.terminate.assert_called_once()
