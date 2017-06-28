from treadmill.infra.instances import Instances


class Node:
    def __init__(self):
        self.instances = None

    def setup(self, Count=1, SubnetId='', SecurityGroupIds=()):
        self.instances = Instances.create(
            Name='TreadmillNode',
            ImageId='ami-9e2f0988',
            Count=Count,
            SubnetId=SubnetId,
            SecurityGroupIds=SecurityGroupIds
        )

        return self.instances

    def terminate(self):
        """Terminate freeipa instance"""
        self.instances.terminate()
