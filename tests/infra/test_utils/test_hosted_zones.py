import unittest
import mock
from treadmill.infra.utils import hosted_zones

class HostedZoneTest(unittest.TestCase):
    @mock.patch('treadmill.infra.connection.Connection')
    def test_delete_record(self, connectionMock):
        hosted_zones.route53_conn = connectionMock()
        record = {
            'Name': 'foo',
            'Type': 'bar',
            'TTL': '100',
            'ResourceRecords': 'somerecords'
        }

        hosted_zones.delete_record('/hostedzone/abc',record)

        hosted_zones.route53_conn.change_resource_record_sets.assert_called_once_with(
            HostedZoneId='abc',
            ChangeBatch={
                'Changes': [{
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': 'foo',
                        'Type': 'bar',
                        'TTL': '100',
                        'ResourceRecords': 'somerecords'
                    }
                }]
            }
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_delete_obsolete(self, connectionMock):
        hosted_zones.route53_conn = connectionMock()
        expected_hosted_zones = [
            {'Id': '/hostedzone/1'}, {'Id': '/hostedzone/2'}, {'Id': '/hostedzone/3'}
        ]
        hosted_zones.route53_conn.list_hosted_zones = mock.Mock(return_value={'HostedZones': expected_hosted_zones})
        hosted_zones.delete_obsolete(('1', '2'))
        hosted_zones.route53_conn.delete_hosted_zone.assert_called_once_with(Id='/hostedzone/3')
