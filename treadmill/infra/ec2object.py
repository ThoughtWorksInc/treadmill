from treadmill.infra import connection
from treadmill.infra import constants


class EC2Object:
    def __init__(self, name=None, id=None, metadata=None, role=None):
        self.id = id
        self.name = name
        self.metadata = metadata
        self.role = role
        self.ec2_conn = connection.Connection()
        self.route53_conn = connection.Connection(
            resource=constants.ROUTE_53
        )
        if self.metadata:
            if self.metadata.get('Tags', None):
                self.name = [t['Value']
                             for t in self.metadata['Tags']
                             if t['Key'] == 'Name'][0]

            _ami_launch_index = self.metadata.get('AmiLaunchIndex', None)
            if self.name and _ami_launch_index is not None:
                self.name = self.name + str(
                    self.metadata['AmiLaunchIndex'] + 1
                )

    def create_tags(self):
        tags = self._prepare_tag_attributes_for('name')

        if self.role:
            tags = tags + self._prepare_tag_attributes_for('role')

        self.ec2_conn.create_tags(
            Resources=[self.id],
            Tags=tags
        )

    def _prepare_tag_attributes_for(self, attr):
        return [{
            'Key': attr.title(),
            'Value': getattr(self, attr)
        }]
