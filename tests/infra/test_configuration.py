"""
Unit test for EC2 configuration.
"""

import unittest
import mock
import io

from treadmill.infra import configuration, SCRIPT_DIR


class ConfigurationTest(unittest.TestCase):
    """Tests configuration"""

    def setUp(self):
        with open(SCRIPT_DIR + 'init.sh', 'r') as data:
            self.init_script_data = data.read()

    @mock.patch('builtins.open', create=True)
    def test_get_userdata(self, open_mock):
        open_mock.side_effect = [
            io.StringIO(self.init_script_data),
            io.StringIO('{{ DOMAIN }}'),
            io.StringIO('{{ CELL }}'),
        ]

        config = configuration.Configuration([])
        userdata = config.get_userdata()
        self.assertEquals(userdata, '')

        config = configuration.Configuration([
            {'name': 'script1.sh', 'vars': {'DOMAIN': 'test.treadmill'}},
            {'name': 'script2.sh', 'vars': {'CELL': 'mycell'}},
        ])
        userdata = config.get_userdata()

        self.assertEquals(
            userdata,
            self.init_script_data + 'test.treadmill\nmycell\n'
        )


class MasterConfigurationTest(unittest.TestCase):
    """Tests master configuration"""

    @mock.patch('builtins.open', create=True)
    def test_master_configuration_script_data(self, open_mock):
        config = configuration.MasterConfiguration('', '', '', '', '', '')
        expected_script_data = {
            'provision-base.sh': [
                'DOMAIN', 'NAME', 'SUBNET_ID', 'LDAP_HOSTNAME', 'APPROOT',
            ],
            'install-treadmill.sh': ['TREADMILL_RELEASE'],
            'configure-master.sh': [],
        }

        self.assertCountEqual(
            [s['name'] for s in config.setup_scripts],
            expected_script_data.keys()
        )

        # Make sure all the scripts have required variables to replace, for
        # jinja
        for script_data in config.setup_scripts:
            self.assertCountEqual(
                expected_script_data[script_data['name']],
                script_data['vars'].keys()
            )


class LDAPConfigurationTest(unittest.TestCase):
    """Tests master configuration"""

    @mock.patch('builtins.open', create=True)
    def test_ldap_configuration_script_data(self, open_mock):
        config = configuration.LDAPConfiguration('', '', '', '', '', '')
        expected_script_data = {
            'provision-base.sh': [
                'DOMAIN', 'NAME', 'SUBNET_ID', 'LDAP_HOSTNAME', 'APPROOT',
            ],
            'install-treadmill.sh': ['TREADMILL_RELEASE'],
            'configure-ldap.sh': ['SUBNET_ID', 'APPROOT'],
        }

        self.assertCountEqual(
            [s['name'] for s in config.setup_scripts],
            expected_script_data.keys()
        )

        # Make sure all the scripts have required variables to replace, for
        # jinja
        for script_data in config.setup_scripts:
            self.assertCountEqual(
                expected_script_data[script_data['name']],
                script_data['vars'].keys()
            )


class IPAConfigurationTest(unittest.TestCase):
    """Tests ipa configuration"""

    @mock.patch('builtins.open', create=True)
    def test_ipa_configuration_script_data(self, open_mock):
        config = configuration.IPAConfiguration(
            ipa_admin_password='admin-password',
            domain='foo.bar',
            tm_release='some-release',
            name='ipa',
            cell='subnet-id',
        )
        expected_script_data = {
            'provision-base.sh': ['DOMAIN', 'NAME'],
            'install-treadmill.sh': ['TREADMILL_RELEASE'],
            'install-ipa-server.sh': [
                'DOMAIN', 'IPA_ADMIN_PASSWORD', 'CELL'
            ],
        }

        self.assertCountEqual(
            [s['name'] for s in config.setup_scripts],
            expected_script_data.keys()
        )

        # Make sure all the scripts have required variables to replace, for
        # jinja
        for script_data in config.setup_scripts:
            self.assertCountEqual(
                expected_script_data[script_data['name']],
                script_data['vars'].keys()
            )
