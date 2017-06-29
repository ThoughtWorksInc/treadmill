"""
Unit test for EC2 configuration.
"""

import unittest
import mock
import io

from treadmill.infra.configuration import Configuration
from treadmill.infra.setup.master import MasterConfiguration
from treadmill.infra import SCRIPT_DIR


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

        configuration = Configuration([])
        userdata = configuration.get_userdata()
        self.assertEquals(userdata, '')

        configuration = Configuration([
            {'name': 'script1.sh', 'vars': {'DOMAIN': 'test.treadmill'}},
            {'name': 'script2.sh', 'vars': {'CELL': 'mycell'}},
        ])
        userdata = configuration.get_userdata()

        self.assertEquals(
            userdata,
            self.init_script_data + 'test.treadmill\nmycell\n'
        )


class MasterConfigurationTest(unittest.TestCase):
    """Tests master configuration"""

    @mock.patch('builtins.open', create=True)
    def test_master_configuration_script_data(self, open_mock):
        configuration = MasterConfiguration('', '', '', '', '')
        expected_script_data = {
            'provision-base.sh': ['DOMAIN', 'NAME'],
            'install-pid1.sh': [],
            'install-s6.sh': [],
            'configure-master.sh': [
                'DOMAIN', 'CELL', 'APPROOT', 'FREEIPA_HOSTNAME',
                'TREADMILL_RELEASE',
            ],
        }

        self.assertCountEqual(
            [s['name'] for s in configuration.setup_scripts],
            expected_script_data.keys()
        )

        # Make sure all the scripts have required variables to replace, for
        # jinja
        for script_data in configuration.setup_scripts:
            self.assertCountEqual(
                expected_script_data[script_data['name']],
                script_data['vars'].keys()
            )
