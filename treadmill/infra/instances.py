from treadmill.infra import connection
import logging

import polling

_LOGGER = logging.getLogger(__name__)


class Instance:
    def __init__(self, Name=None, id=None, metadata=None):
        self.id = id
        self.name = Name
        self.metadata = metadata
        self.conn = connection.Connection()

        if self.metadata and self.metadata.get('Tags', None):
            self.name = [t['Value']
                         for t in self.metadata['Tags']
                         if t['Key'] == 'Name'][0]

        self.private_ip = self.metadata.get(
            'PrivateIpAddress',
            ''
        ) if metadata else ''

    def create_tags(self):
        self.name = self.name + str(
            self.metadata.get('AmiLaunchIndex', 0) + 1
        )
        self.conn.create_tags(
            Resources=[self.id],
            Tags=[{
                'Key': 'Name',
                'Value': self.name
            }]
        )

    def upsert_dns_record(self, hosted_zone_id, domain='', Reverse=False):
        self._change_resource_record_sets(
            'UPSERT',
            hosted_zone_id,
            domain,
            Reverse
        )

    def delete_dns_record(self, hosted_zone_id, domain='', Reverse=False):
        self._change_resource_record_sets(
            'DELETE',
            hosted_zone_id,
            domain,
            Reverse
        )

    def _change_resource_record_sets(
            self,
            action,
            hosted_zone_id,
            domain='',
            Reverse=False
    ):
        if Reverse:
            _name, _type, _value = self._reverse_dns_record_attrs(domain)
        else:
            _name, _type, _value = self._forward_dns_record_attrs(domain)

        _conn = connection.Connection('route53')
        _conn.change_resource_record_sets(
            HostedZoneId=hosted_zone_id.split('/')[-1],
            ChangeBatch={
                'Changes': [{
                    'Action': action,
                    'ResourceRecordSet': {
                        'Name': _name,
                        'Type': _type,
                        'TTL': 3600,
                        'ResourceRecords': [{
                            'Value': _value
                        }]
                    }
                }]
            }
        )

    def _reverse_dns_record_attrs(self, domain):
        forward_dns_name = self.name.lower() + '.' + domain + '.'
        return [
            self._reverse_dns_record_name(),
            'PTR',
            forward_dns_name
        ]

    def _forward_dns_record_attrs(self, domain):
        forward_dns_name = self.name.lower() + '.' + domain + '.'
        return [
            forward_dns_name,
            'A',
            self.private_ip
        ]

    def _reverse_dns_record_name(self):
        ip_octets = self.private_ip.split('.')
        ip_octets.reverse()
        ip_octets.append('in-addr.arpa')

        return '.'.join(ip_octets)


class Instances:
    def __init__(self, instances):
        self.instances = instances
        self.volume_ids = []
        self.conn = connection.Connection()

    @property
    def ids(self):
        return [i.id for i in self.instances]

    @classmethod
    def load_json(cls, ids=None, filters=None):
        """Fetch instance details"""
        conn = connection.Connection()
        response = []

        if ids:
            response = conn.describe_instances(
                InstanceIds=ids
            )['Reservations']
        elif filters:
            response = conn.describe_instances(
                Filters=filters
            )['Reservations']
        else:
            return []

        return sum([r['Instances'] for r in response], [])

    @classmethod
    def get(cls, ids=None, filters=None):
        json = Instances.load_json(ids=ids, filters=filters)
        return Instances(
            instances=[Instance(
                id=j['InstanceId'],
                metadata=j
            ) for j in json]
        )

    @classmethod
    def create(cls, Name=None, ImageId=None,
               InstanceType='t2.small', SubnetId='',
               Count=1, SecurityGroupIds=None, KeyName='ms_treadmill_dev',
               UserData=''):
        conn = connection.Connection()
        _instances = conn.run_instances(
            ImageId=ImageId,
            MinCount=Count,
            MaxCount=Count,
            InstanceType=InstanceType,
            SubnetId=SubnetId,
            SecurityGroupIds=SecurityGroupIds,
            KeyName=KeyName,
            UserData=UserData,
        )

        _ids = [i['InstanceId'] for i in _instances['Instances']]
        _instances_json = Instances.load_json(ids=_ids)

        _instances = []
        for i in _instances_json:
            _instance = Instance(
                id=i['InstanceId'],
                Name=Name,
                metadata=i
            )
            _instance.create_tags()
            _instances.append(_instance)

        return Instances(instances=_instances)

    create_master = create_freeipa = create_node = create

    def get_volume_ids(self):
        if not self.volume_ids:
            volumes = self.conn.describe_volumes(
                Filters=[{
                    'Name': 'attachment.instance-id',
                    'Values': self.ids
                }]
            )
            self.volume_ids = [v['VolumeId'] for v in volumes['Volumes']]

    def terminate(self, hosted_zone_id, reverse_hosted_zone_id, domain):
        self.get_volume_ids()
        for instance in self.instances:
            instance.delete_dns_record(
                hosted_zone_id,
                domain
            )
            instance.delete_dns_record(
                hosted_zone_id=reverse_hosted_zone_id,
                domain=domain,
                Reverse=True
            )
        self.conn.terminate_instances(
            InstanceIds=self.ids
        )
        self._wait_for_termination()
        self.delete_volumes()

    def delete_volumes(self):
        for volume_id in self.volume_ids:
            self.conn.delete_volume(VolumeId=volume_id)

    def _wait_for_termination(self):
        if len(self.ids) == 0:
            return

        def is_terminated(res):
            _LOGGER.info("\nWaiting for instances termination...")
            _LOGGER.info("Current states:")
            instance_data = [
                status['InstanceId'] + ": " + status['InstanceState']['Name']
                for status in res['InstanceStatuses']
            ]
            _LOGGER.info("\n".join(instance_data))

            instance_statuses = list(set(
                [
                    status['InstanceState']['Name']
                    for status in res['InstanceStatuses']
                ]
            ))

            status_len = len(instance_statuses)
            return (
                status_len == 0
            ) or (
                status_len == 1 and instance_statuses[0] == 'terminated'
            )

        if polling.poll(
            lambda: self.conn.describe_instance_status(
                InstanceIds=self.ids,
                IncludeAllInstances=True
            ),
            check_success=is_terminated,
            step=10,
            timeout=300
        ):
            return
