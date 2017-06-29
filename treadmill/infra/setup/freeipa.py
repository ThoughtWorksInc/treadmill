from treadmill.infra import instances


class FreeIPA:
    def __init__(self):
        self.instance = None

    def setup(self, name, image_id, count, subnet_id):
        self.instances = instances.Instances.create(
            Name=name,
            ImageId=image_id,
            Count=count,
            SubnetId=subnet_id,
        )

    def terminate(self):
        """Terminate freeipa instance"""
        self.instances.terminate()
