from treadmill.infra import instances


class FreeIPA:
    def __init__(self):
        self.instance = None

    def setup(self, Name, ImageId, Count, SubnetId):
        self.instances = instances.Instances.create(
            Name=Name,
            ImageId=ImageId,
            Count=Count,
            SubnetId=SubnetId,
        )

    def terminate(self):
        """Terminate freeipa instance"""
        self.instances.terminate()
