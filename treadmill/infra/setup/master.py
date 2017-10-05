from treadmill.infra.setup import base_provision
from treadmill.infra import configuration, constants
from treadmill.api import ipa


class Master(base_provision.BaseProvision):
    def setup(
            self,
            image,
            count,
            cidr_block,
            tm_release,
            key,
            instance_type,
            app_root,
            ipa_admin_password,
            proid,
            subnet_name,
    ):
        ldap_hostname, = self.hostnames_for(roles=[constants.ROLES['LDAP']])

        _ipa = ipa.API()
        _master_hostnames = self._hostname_cluster(count)

        for _master_h in _master_hostnames.keys():
            _otp = _ipa.add_host(hostname=_master_h)
            _idx = _master_hostnames[_master_h]
            self.name = _master_h

            self.configuration = configuration.Master(
                hostname=_master_h,
                otp=_otp,
                ldap_hostname=ldap_hostname,
                tm_release=tm_release,
                app_root=app_root,
                ipa_admin_password=ipa_admin_password,
                idx=_idx,
                proid=proid
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
