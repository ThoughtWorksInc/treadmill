from jinja2 import Template

from treadmill.infra import SCRIPT_DIR


class Configuration:
    """Configure instances"""

    def __init__(self, setup_scripts=None):
        self.setup_scripts = setup_scripts or []

    def get_userdata(self):
        if not self.setup_scripts:
            return ''

        userdata = ''
        # Add initializer script
        self.setup_scripts.insert(0, {'name': 'init.sh'})
        for script in self.setup_scripts:
            with open(SCRIPT_DIR + script['name'], 'r') as data:
                template = Template(data.read())
                userdata += template.render(script.get('vars', {})) + '\n'
        return userdata


class MasterConfiguration(Configuration):
    def __init__(self, name, domain, subnet_id,
                 app_root, ldap_hostname, tm_release):
        self.setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': domain,
                    'SUBNET_ID': subnet_id,
                    'APPROOT': app_root,
                    'LDAP_HOSTNAME': ldap_hostname,
                    'NAME': name,
                },
            }, {
                'name': 'install-treadmill.sh',
                'vars': {'TREADMILL_RELEASE': tm_release}
            }, {
                'name': 'configure-master.sh',
                'vars': {},
            },
        ]
        super(MasterConfiguration, self).__init__(self.setup_scripts)


class LDAPConfiguration(Configuration):
    def __init__(self, name, domain, subnet_id, tm_release, app_root,
                 ldap_hostname):
        self.setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': domain,
                    'NAME': name,
                    'SUBNET_ID': subnet_id,
                    'APPROOT': app_root,
                    'LDAP_HOSTNAME': ldap_hostname,
                },
            }, {
                'name': 'install-treadmill.sh',
                'vars': {'TREADMILL_RELEASE': tm_release}
            }, {
                'name': 'configure-ldap.sh',
                'vars': {
                    'SUBNET_ID': subnet_id,
                    'APPROOT': app_root,
                },
            },
        ]
        super(LDAPConfiguration, self).__init__(self.setup_scripts)


class IPAConfiguration(Configuration):
    def __init__(self, name, cell, ipa_admin_password, domain, tm_release):
        self.setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': domain,
                    'NAME': name,
                },
            }, {
                'name': 'install-treadmill.sh',
                'vars': {'TREADMILL_RELEASE': tm_release}
            }, {
                'name': 'install-ipa-server.sh',
                'vars': {
                    'DOMAIN': domain,
                    'IPA_ADMIN_PASSWORD': ipa_admin_password,
                    'CELL': cell
                },
            },
        ]
        super(IPAConfiguration, self).__init__(self.setup_scripts)
