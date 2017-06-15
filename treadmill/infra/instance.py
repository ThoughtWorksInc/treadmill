from treadmill.infra.connection import Connection
import polling


class Instance:
    def __init__(self, Name=None, ImageId=None,
                 InstanceType='t2.small', SubnetId='',
                 Count=1, SecurityGroupIds=None, ids=None):
        self.ids = ids or []
        self.name = Name
        self.conn = Connection()
        self.ImageId = ImageId
        self.InstanceType = InstanceType
        self.SubnetId = SubnetId
        self.count = Count
        self.SecurityGroupIds = SecurityGroupIds or None
        self.volume_ids = []

    @classmethod
    def load_json(cls, ids=[], filters=[]):
        """Fetch instance details"""
        conn = Connection()

        if ids:
            response = conn.describe_instances(
                InstanceIds=ids
            )['Reservations']
        elif filters:
            response = conn.describe_instances(
                Filters=filters
            )['Reservations']

        return sum([r['Instances'] for r in response], [])

    def create(self):
        self.instances = self.conn.run_instances(
            ImageId=self.ImageId,
            MinCount=self.count,
            MaxCount=self.count,
            InstanceType=self.InstanceType,
            SubnetId=self.SubnetId,
            SecurityGroupIds=self.SecurityGroupIds
        )

        self.ids = [i['InstanceId'] for i in self.instances['Instances']]

        for idx, id in enumerate(self.ids, start=1):
            tag_name = self.name + str(idx)
            self.conn.create_tags(
                Resources=[id],
                Tags=[{
                    'Key': 'Name',
                    'Value': tag_name
                }]
            )

    create_master = create_freeipa = create_node = create

    def terminate(self):
        self.get_volume_ids()
        self.conn.terminate_instances(InstanceIds=self.ids)
        self._wait_for_termination()
        self.delete_volumes()

    def get_volume_ids(self):
        if not self.volume_ids:
            volumes = self.conn.describe_volumes(
                Filters=[{
                    'Name': 'attachment.instance-id',
                    'Values': self.ids
                }]
            )
            self.volume_ids = [v['VolumeId'] for v in volumes['Volumes']]

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
