from treadmill.infra.setup import base_provision
from treadmill.infra import configuration, constants
from treadmill.api import ipa


class Zookeeper(base_provision.BaseProvision):
    def setup(self, image, key, cidr_block, instance_type,
              ipa_admin_password, proid, subnet_name, count=3):
        ldap_hostname, ipa_server_hostname = self.hostnames_for(
            roles=[
                constants.ROLES['IPA'],
                constants.ROLES['LDAP'],
            ]
        )
        _ipa = ipa.API()
        _zk_hostnames = self._hostname_cluster(count=count)

        for _zk_h in _zk_hostnames.keys():
            _otp = _ipa.add_host(hostname=_zk_h)
            _idx = _zk_hostnames[_zk_h]
            self.name = _zk_h

            self.configuration = configuration.Zookeeper(
                ldap_hostname=ldap_hostname,
                ipa_server_hostname=ipa_server_hostname,
                hostname=_zk_h,
                otp=_otp,
                idx=_idx,
                proid=proid,
            )

            super().setup(
                image=image,
                count=1,
                cidr_block=cidr_block,
                key=key,
                instance_type=instance_type,
                subnet_name=subnet_name,
                sg_names=[constants.COMMON_SEC_GRP],
            )
