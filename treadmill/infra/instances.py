from treadmill.infra.connection import Connection

import polling


class Instance:
    def __init__(self, Name=None, id=None, metadata=None):
        self.id = id
        self.name = Name
        self.conn = Connection()
        self.metadata = metadata
        self.private_ip = metadata.get('PrivateIpAddress', '') if metadata else ''

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

    def upsert_dns_record(self, hosted_zone_id, Region, Reverse=False):
        _name, _type, _value = [
            self._reverse_dns_record_name(), 'PTR', self.name
        ] if Reverse else [
            self.name, 'A', self.private_ip
        ]

        _conn = Connection('route53')
        _conn.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': _name,
                        'Type': _type,
                        'Region': Region,
                        'ResourceRecords': [{
                            'Value': _value
                        }]
                    }
                }]
            }
        )

    def _reverse_dns_record_name(self):
        ip_octets = self.private_ip.split('.')
        ip_octets.reverse()
        ip_octets.append('in-addr.arpa')

        return '.'.join(ip_octets)


class Instances:
    def __init__(self, instances):
        self.instances = instances
        self.volume_ids = []
        self.conn = Connection()

    @property
    def ids(self):
        return [i.id for i in self.instances]

    @classmethod
    def load_json(cls, ids=[], filters=[]):
        """Fetch instance details"""
        conn = Connection()
        response = []

        if ids:
            response = conn.describe_instances(
                InstanceIds=ids
            )['Reservations']
        elif filters:
            response = conn.describe_instances(
                Filters=filters
            )['Reservations']

        return sum([r['Instances'] for r in response], [])

    @classmethod
    def get(cls, ids=[], filters=[]):
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
        conn = Connection()
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

    def terminate(self):
        self.get_volume_ids()
        self.conn.terminate_instances(InstanceIds=self.ids)
        self._wait_for_termination()
        self.delete_volumes()

    def delete_volumes(self):
        for volume_id in self.volume_ids:
            self.conn.delete_volume(VolumeId=volume_id)

    def _wait_for_termination(self):
        if len(self.ids) == 0:
            return

        def is_terminated(res):
            print("\nWaiting for instances termination...")
            print("Current states:")
            instance_data = [
                status['InstanceId'] + ": " + status['InstanceState']['Name']
                for status in res['InstanceStatuses']
            ]
            print("\n".join(instance_data))

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
            timeout=120
        ):
            return
