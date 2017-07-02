from treadmill.infra import instances
from treadmill.infra import connection
from treadmill.infra import vpc
from treadmill.infra import constants


class FreeIPA:
    def __init__(self):
        pass

    def setup(self, name, image_id, count, subnet_id, vpc_id, domain):
        self.conn = connection.Connection('route53')
        self.name = name
        self.domain = domain
        self.instances = instances.Instances.create(
            name=self.name,
            image_id=image_id,
            count=count,
            subnet_id=subnet_id,
            instance_type=constants.INSTANCE_TYPES['EC2']['medium']
        )

        self._update_route53('UPSERT', vpc_id, domain)

    def destroy(self):
        """Terminate freeipa instance"""
        self.instances.terminate()

    def _update_route53(self, action, vpc_id, domain):
        _vpc = vpc.VPC(vpc_id)
        _vpc.get_hosted_zone_ids()

        srv_records = {
            '_kerberos-master._tcp': '0 100 88',
            '_kerberos-master._udp': '0 100 88',
            '_kerberos._tcp': '0 100 88',
            '_kerberos._udp': '0 100 88',
            '_kpasswd._tcp': '0 100 464',
            '_kpasswd._udp': '0 100 464',
            '_ldap._tcp': '0 100 389',
            '_ntp._udp': '0 100 123'
        }

        for _rec, _value in srv_records.items():
            self._change_srv_record(
                action=action,
                hosted_zone_id=_vpc.hosted_zone_id,
                name=self._rec_name(_rec),
                value=self._srv_rec_value(_value),
                record_type='SRV'
            )

        self._change_srv_record(
            action=action,
            hosted_zone_id=_vpc.hosted_zone_id,
            name=self._rec_name('ipa-ca'),
            value=self.instances.instances[0].private_ip,
            record_type='A'
        )
        self._change_srv_record(
            action=action,
            hosted_zone_id=_vpc.hosted_zone_id,
            name=self._rec_name('_kerberos'),
            value='"{0}"'.format(domain.upper()),
            record_type='TXT'
        )

    def _rec_name(self, name):
        return name + '.' + self.domain + '.'

    def _srv_rec_value(self, value):
        return value + ' ' + self.name + '.' + self.domain + '.'

    def _change_srv_record(self,
                           action,
                           hosted_zone_id,
                           name,
                           value,
                           record_type):
        self.conn.change_resource_record_sets(
            HostedZoneId=hosted_zone_id.split('/')[-1],
            ChangeBatch={
                'Changes': [{
                    'Action': action,
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': record_type,
                        'TTL': constants.IPA_ROUTE_53_RECORD_SET_TTL,
                        'ResourceRecords': [{
                            'Value': value
                        }]
                    }
                }]
            }
        )
