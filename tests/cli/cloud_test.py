import importlib
import unittest
import click
import click.testing
import mock

from treadmill.infra import constants


class CloudTest(unittest.TestCase):
    def setUp(self):
        self.runner = click.testing.CliRunner()
        self.configure_cli = importlib.import_module(
            'treadmill.cli.cloud').init()

    @mock.patch('treadmill.cli.cloud.Cell')
    def test_init(self, cell_mock):
        """
        Test cloud init
        """
        cell = cell_mock()
        result = self.runner.invoke(
            self.configure_cli, [
                'init',
                '--vpc-id=vpc-123',
                '--domain=test.treadmill',
                '--region=us-west-1',
                '--vpc-cidr-block=172.24.0.0/16',
                '--secgroup_name=sg_common',
                '--secgroup_desc=Test'
            ])

        self.assertEqual(result.exit_code, 0)
        cell.setup_vpc.assert_called_once_with(
            vpc_cidr_block='172.24.0.0/16',
            secgroup_name='sg_common',
            secgroup_desc='Test'
        )

    @mock.patch('treadmill.cli.cloud.Cell')
    def test_init_cell(self, cell_mock):
        """
        Test cloud init cell
        """
        cell = cell_mock()
        result = self.runner.invoke(
            self.configure_cli, [
                'init-cell',
                '--key=key',
                '--image-id=img-123',
                '--subnet-id=sub-123',
                '--vpc-id=vpc-123',
                '--cell-cidr-block=172.24.0.0/24'
            ])

        self.assertEqual(result.exit_code, 0)
        cell.setup_master.assert_called_once_with(
            name='TreadmillMaster',
            key='key',
            count=3,
            image_id='img-123',
            instance_type=constants.INSTANCE_TYPES['EC2']['micro'],
            tm_release='0.1.0',
            ldap_hostname='ldapserver',
            app_root='/var/tmp/',
            subnet_cidr_block='172.24.0.0/24',
        )
