from treadmill.infra.setup import base_provision
from treadmill.infra import configuration, constants
from treadmill.infra import instances
from treadmill.api import ipa


class Zookeeper(base_provision.BaseProvision):
    def setup(self, image, key, cidr_block, instance_type,
              ipa_admin_password, proid, subnet_name):
        _hostnames = instances.Instances.get_hostnames_by_roles(
            vpc_id=self.vpc.id,
            roles=[
                constants.ROLES['IPA'],
                constants.ROLES['LDAP'],
            ]
        )

        _ipa = ipa.API()
        _zk_hostnames = self._hostname_cluster(count=3)

        _name = self.name
        for _zk_h in _zk_hostnames.keys():
            _otp = _ipa.add_host(hostname=_zk_h)
            _idx = _zk_hostnames[_zk_h]
            self.configuration = configuration.Zookeeper(
                ldap_hostname=_hostnames[constants.ROLES['LDAP']],
                ipa_server_hostname=_hostnames[constants.ROLES['IPA']],
                hostname=_zk_h,
                otp=_otp,
                idx=_idx,
                proid=proid,
            )

            self.name = _name + _idx
            super().setup(
                image=image,
                count=1,
                cidr_block=cidr_block,
                key=key,
                instance_type=instance_type,
                subnet_name=subnet_name,
            )
