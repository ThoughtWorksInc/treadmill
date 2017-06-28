import importlib
import unittest
import click
import click.testing
import mock


class CloudTest(unittest.TestCase):
    def setUp(self):
        self.runner = click.testing.CliRunner()
        self.configure_cli = importlib.import_module(
            'treadmill.cli.cloud').init()

    @mock.patch('treadmill.cli.cloud.Cell')
    def test_init_without_cell(self, cell_mock):
        cell = cell_mock()
        result = self.runner.invoke(
            self.configure_cli, [
                'init',
                '--domain=test.treadmill',
                '--region=us-west-1',
                '--vpc-cidr-block=172.24.0.0/16',
                '--subnet-cidr-block=172.24.0.0/24',
                '--security-group-name=sg_common2',
                '--security-group-description=Test'
            ])

        self.assertEqual(result.exit_code, 0)
        cell.vpc_setup.assert_called_once_with(
            domain='test.treadmill',
            region_name='us-west-1',
            vpc_cidr_block='172.24.0.0/16',
            subnet_cidr_block='172.24.0.0/24',
            security_group_name='sg_common2',
            security_group_description='Test'
        )
