from treadmill.infra.instance import Instance


class FreeIPA:
    def __init__(self):
        self.instance = None

    def setup(self, SubnetId=''):
        self.instance = Instance(
            'TreadmillFreeIPA',
            ImageId='ami-6d1c2007',
            Count=1,
            SubnetId=SubnetId,
        )
        self.instance.create_freeipa()

    def terminate(self):
        """Terminate freeipa instance"""
        self.instance.terminate()
