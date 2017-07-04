from treadmill.infra import instances
from treadmill.infra import connection
from treadmill.infra import vpc
from treadmill.infra import constants


class IPA:
    def __init__(
            self,
            name,
            vpc_id,
            domain,
            region_name
    ):
        self.name = name
        self.vpc_id = vpc_id
        self.domain = domain
        self.region_name = region_name
        self.route_53_conn = connection.Connection('route53')

    def setup(self,
              image_id,
              count,
              subnet_id):
        self.instances = instances.Instances.create(
            name=self.name,
            image_id=image_id,
            count=count,
            subnet_id=subnet_id,
            instance_type=constants.INSTANCE_TYPES['EC2']['medium']
        )

        self._update_route53('UPSERT')

    def destroy(self, instance_id):
        """Terminate ipa instance"""
        self.instances = instances.Instances.get(ids=[instance_id])
        self._update_route53('DELETE')
        self.instances.terminate(
            hosted_zone_id=self.vpc.hosted_zone_id,
            reverse_hosted_zone_id=self.vpc.reverse_hosted_zone_id,
            domain=self.domain
        )

    def _update_route53(self, action):
        self.vpc = vpc.VPC(
            id=self.vpc_id,
            domain=self.domain,
            region_name=self.region_name
        )
        self.vpc.get_hosted_zone_ids()

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
                hosted_zone_id=self.vpc.hosted_zone_id,
                name=self._rec_name(_rec),
                value=self._srv_rec_value(_value),
                record_type='SRV'
            )
        self._change_srv_record(
            action=action,
            hosted_zone_id=self.vpc.hosted_zone_id,
            name=self._rec_name('ipa-ca'),
            value=self.instances.instances[0].private_ip,
            record_type='A'
        )
        self._change_srv_record(
            action=action,
            hosted_zone_id=self.vpc.hosted_zone_id,
            name=self._rec_name('_kerberos'),
            value='"{0}"'.format(self.domain.upper()),
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
        self.route_53_conn.change_resource_record_sets(
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
