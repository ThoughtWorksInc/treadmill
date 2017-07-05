from treadmill.infra import ec2object
from treadmill.infra import connection


class Subnet(ec2object.EC2Object):
    def __init__(self, name=None, id=None, metadata=None, vpc_id=None):
        super(Subnet, self).__init__(
            name=name,
            id=id,
            metadata=metadata
        )
        self.vpc_id = vpc_id

    @classmethod
    def create(cls, cidr_block, vpc_id, name):
        _ec2_conn = connection.Connection()
        response = _ec2_conn.create_subnet(
            VpcId=vpc_id,
            CidrBlock=cidr_block,
            AvailabilityZone=Subnet._availability_zone()
        )
        _subnet = Subnet(
            id=response['Subnet']['SubnetId'],
            name=name,
            metadata=response,
            vpc_id=vpc_id
        )
        _subnet.create_tags()
        return _subnet

    @classmethod
    def _availability_zone(cls):
        _map = {
            "us-east-1": "us-east-1a",
            "us-east-2": "us-east-2a",
            "ap-southeast-1": "ap-southeast-1a",
            "ap-southeast-2": "ap-southeast-2a",
            "us-west-1": "us-west-1b",
            "us-west-2": "us-west-2a"
        }

        return _map.get(connection.Connection.region_name, None)
