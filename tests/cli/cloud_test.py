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

    @mock.patch('treadmill.cli.cloud.VPC')
    def test_init_without_cell(self, vpc_mock):
        _vpc = vpc_mock()

        _result = self.runner.invoke(
            self.configure_cli,
            ['init']
        )

        self.assertEqual(_result.exit_code, 0)
        _vpc.create.assert_called_once()
        _vpc.create_subnet.assert_called_once()
        _vpc.create_internet_gateway.assert_called_once()
        _vpc.create_route_table.assert_called_once()
        _vpc.create_security_group.assert_called_once_with(
            'sg_common',
            'Treadmill Security group'
        )
        _vpc.create_hosted_zone.assert_called_once()

    @mock.patch('treadmill.cli.cloud.Master')
    def test_init_with_cell(self, master_mock):
        _master = master_mock()
        result = self.runner.invoke(
            self.configure_cli,
            ['init', '--cell']
        )

        self.assertEqual(result.exit_code, 0)
        _master.setup.assert_called_once()
