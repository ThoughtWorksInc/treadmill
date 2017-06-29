from treadmill.infra import instances


class Node:
    def __init__(self):
        self.instances = None

    def setup(self, Name, ImageId, Count, SubnetId, SecurityGroupIds):
        self.instances = instances.Instances.create(
            Name=Name,
            ImageId=ImageId,
            Count=Count,
            SubnetId=SubnetId,
            SecurityGroupIds=SecurityGroupIds
        )

        return self.instances

    def terminate(self):
        """Terminate freeipa instance"""
        self.instances.terminate()
