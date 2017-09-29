from treadmill.infra import instances
from treadmill.infra import connection
from treadmill.infra import vpc
from treadmill.infra import subnet
from treadmill.infra import constants


class BaseProvision:
    def __init__(
            self,
            name,
            vpc_id
    ):
        self.name = name
        self.vpc = vpc.VPC(id=vpc_id)
        self.ec2_conn = connection.Connection()
        _role = constants.ROLES.get(
            self.__class__.__name__.upper(),
            'DEFAULT'
        )
        self.role = _role
        self.subnet = None

    def setup(
            self,
            image,
            count,
            key,
            instance_type,
            subnet_name,
            cidr_block=None,
    ):
        if not self.subnet:
            self.subnet = subnet.Subnet.get(
                name=subnet_name,
                vpc_id=self.vpc.id
            )

        if not self.subnet.persisted and not cidr_block:
            raise Exception(
                'Subnet CIDR block required for creating new subnet'
            )

        if not self.subnet.persisted:
            self.vpc.load_internet_gateway_ids()
            if not self.subnet.persisted:
                self.subnet.persist(
                    cidr_block=cidr_block,
                    gateway_id=self.vpc.gateway_ids[0]
                )

        user_data = ''
        if getattr(self, 'configuration', None):
            self.configuration.subnet_id = self.subnet.id
            user_data = self.configuration.get_userdata()

        self.vpc.load_security_group_ids()

        self.subnet.instances = instances.Instances.create(
            name=self.name,
            image=image,
            count=count,
            subnet_id=self.subnet.id,
            instance_type=instance_type,
            key_name=key,
            secgroup_ids=self.vpc.secgroup_ids,
            user_data=user_data,
            role=self.role
        )

    def destroy(self, subnet_name=None):
        if subnet_name:
            self.subnet = subnet.Subnet(name=subnet_name)
            self.subnet.destroy(role=self.role)
        else:
            _instances = instances.Instances.get_by_roles(
                vpc_id=self.vpc.id,
                roles=[self.role]
            )

            _subnet_ids = set(_i.subnet_id for _i in _instances.instances)

            _instances.terminate()

            [
                subnet.Subnet(
                    id=_id,
                    role=self.role
                ).destroy() for _id in _subnet_ids
            ]

    def show(self):
        return self.subnet.show()

    def _hostname_cluster(self, count):
        _hostnames = {}

        for _idx in range(0, count):
            _idx_s = str(_idx + 1)
            _hostnames[
                self.name + _idx_s + '.' + connection.Connection.context.domain
            ] = _idx_s

        return _hostnames
