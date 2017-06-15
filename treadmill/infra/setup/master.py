from treadmill.infra.vpc import VPC
from treadmill.infra.instance import Instance


class Master:
    def __init__(self, vpc_id=None):
        self.vpc = VPC(vpc_id)

    def setup(self):
        if not self.vpc.id:
            self.vpc.create()

        self.vpc.create_subnet()
        self.vpc.create_internet_gateway()
        self.vpc.create_route_table()
        self.vpc.create_security_group('sg_common', 'Treadmill Security group')
        self.vpc.create_hosted_zone()

        instance = Instance(
            'TreadmillMaster',
            ImageId='ami-6d1c2007',
            Count=3,
            SubnetId=self.vpc.subnet_ids[0],
            SecurityGroupIds=self.vpc.secgroup_ids
        )

        instance.create_master()

        self.vpc.instance_ids = instance.ids
        self.ids = instance.ids
        self.show()

        return self.vpc.id

    def destroy(self):
        try:
            self.vpc.terminate_instances()
        except Exception as ex:
            print("Error: {0}".format(ex))

        self.vpc.delete_internet_gateway()
        self.vpc.delete_security_groups()
        self.vpc.delete_route_tables()
        self.vpc.delete()
        self.vpc.delete_hosted_zone()

    def show(self):
        self.output = self.vpc.show()
        print("******************************************************")
        print(self.output)
        print("******************************************************")
