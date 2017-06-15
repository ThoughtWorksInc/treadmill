from treadmill.infra.instance import Instance


class Node:
    def __init__(self):
        self.instances = None

    def setup(self, Count=1, SubnetId='', SecurityGroupIds=()):
        self.instances = Instance(
            'TreadmillNode',
            ImageId='ami-6d1c2007',
            Count=Count,
            SubnetId=SubnetId,
            SecurityGroupIds=SecurityGroupIds
        )

        self.instances.create_node()
        return self.instances

    def terminate(self):
        """Terminate freeipa instance"""
        self.instances.terminate()
