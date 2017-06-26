from treadmill.infra.instances import Instances


class FreeIPA:
    def __init__(self):
        self.instance = None

    def setup(self, SubnetId=''):
        self.instances = Instances.create(
            Name='TreadmillFreeIPA',
            ImageId='ami-6d1c2007',
            Count=1,
            SubnetId=SubnetId,
        )

    def terminate(self):
        """Terminate freeipa instance"""
        self.instances.terminate()
