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
