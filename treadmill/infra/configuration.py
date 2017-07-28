from jinja2 import Template

from treadmill.infra import SCRIPT_DIR
from treadmill.infra import connection


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


class Master(Configuration):
    def __init__(self, name, subnet_id,
                 app_root, ldap_hostname, tm_release):
        setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': connection.Connection.context.domain,
                    'SUBNET_ID': subnet_id,
                    'APP_ROOT': app_root,
                    'LDAP_HOSTNAME': ldap_hostname,
                    'NAME': name,
                },
            }, {
                'name': 'install-ipa-client.sh',
                'vars': {}
            }, {
                'name': 'install-treadmill.sh',
                'vars': {'TREADMILL_RELEASE': tm_release}
            }, {
                'name': 'configure-master.sh',
                'vars': {
                    'SUBNET_ID': subnet_id,
                },
            },
        ]
        super().__init__(setup_scripts)


class LDAP(Configuration):
    def __init__(self, name, cell_subnet_id, tm_release, app_root,
                 ldap_hostname, ipa_admin_password):
        setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': connection.Connection.context.domain,
                    'NAME': name,
                    'SUBNET_ID': cell_subnet_id,
                    'APP_ROOT': app_root,
                    'LDAP_HOSTNAME': ldap_hostname,
                },
            }, {
                'name': 'install-ipa-client.sh',
                'vars': {}
            }, {
                'name': 'install-treadmill.sh',
                'vars': {'TREADMILL_RELEASE': tm_release}
            }, {
                'name': 'configure-ldap.sh',
                'vars': {
                    'SUBNET_ID': cell_subnet_id,
                    'APP_ROOT': app_root,
                    'IPA_ADMIN_PASSWORD': ipa_admin_password,
                    'DOMAIN': connection.Connection.context.domain,
                },
            },
        ]
        super().__init__(setup_scripts)


class IPA(Configuration):
    def __init__(self, name, cell, ipa_admin_password, tm_release):
        setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': connection.Connection.context.domain,
                    'NAME': name,
                },
            }, {
                'name': 'install-treadmill.sh',
                'vars': {'TREADMILL_RELEASE': tm_release}
            }, {
                'name': 'install-ipa-server.sh',
                'vars': {
                    'DOMAIN': connection.Connection.context.domain,
                    'IPA_ADMIN_PASSWORD': ipa_admin_password,
                    'CELL': cell
                },
            },
        ]
        super().__init__(setup_scripts)


class Zookeeper(Configuration):
    def __init__(self, name):
        setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': connection.Connection.context.domain,
                    'NAME': name,
                },
            }, {
                'name': 'install-ipa-client.sh',
                'vars': {}
            }, {
                'name': 'provision-zookeeper.sh',
                'vars': {
                    'DOMAIN': connection.Connection.context.domain,
                },
            },
        ]
        super().__init__(setup_scripts)


class Node(Configuration):
    def __init__(self, name, tm_release, app_root, subnet_id,
                 ldap_hostname):
        setup_scripts = [
            {
                'name': 'provision-base.sh',
                'vars': {
                    'DOMAIN': connection.Connection.context.domain,
                    'NAME': name,
                    'APP_ROOT': app_root,
                    'SUBNET_ID': subnet_id,
                    'LDAP_HOSTNAME': ldap_hostname,
                }
            }, {
                'name': 'install-ipa-client.sh',
                'vars': {}
            }, {
                'name': 'install-treadmill.sh',
                'vars': {
                    'TREADMILL_RELEASE': tm_release
                }
            }, {
                'name': 'configure-node.sh',
                'vars': {
                    'APP_ROOT': app_root,
                },
            }
        ]
        super().__init__(setup_scripts)
