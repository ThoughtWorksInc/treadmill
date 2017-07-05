"""
Unit test for EC2 cell setup.
"""

import unittest
from treadmill.infra.setup.cell import Cell
from treadmill.infra import constants


class CellTest(unittest.TestCase):
    """Tests EC2 cell setup."""

    def setUp(self):
        self.cell = Cell(domain='ms.treadmill')

    def tearDown(self):
        self.cell.vpc.delete()

    def test_setup_cell(self):
        self.cell.setup_vpc(
            vpc_cidr_block='172.23.0.0/16',
            cell_cidr_block='172.23.0.0/24',
            secgroup_name='sg_common',
            secgroup_desc='Treadmill CIDR block'
        )
        self.vpc_id = self.cell.setup_master(
            name='TreadmillMaster',
            image_id='ami-9e2f0988',
            count=3,
            tm_release='0.1.0',
            ipa_hostname='ipa',
            key_name='ms_treadmill_dev',
            instance_type=constants.INSTANCE_TYPES['EC2']['small'],
            app_root='/var/tmp',
        )
        output = self.cell.output

        self.assertEquals(len(self.cell.ids), 3)
        self.assertIsNotNone(self.vpc_id)
        self.assertIsNotNone(self.cell.vpc.hosted_zone_id)
        self.assertIsNotNone(self.cell.vpc.reverse_hosted_zone_id)
        self.assertEquals(output['VpcId'], self.vpc_id)
        self.assertEquals(len(output['Instances']), 3)
        for instance in output['Instances']:
            self.assertIsNotNone(instance['InstanceId'])
            self.assertIsNotNone(instance['CellId'])
            self.assertIsNotNone(instance['SecurityGroups'])
            self.assertIn(instance['InstanceState'], ['pending', 'running'])
            self.assertIn(instance['CellId'], self.cell.cell.id)

        self.cell.destroy()

        self.cell.cell.instances = None
        self.cell.cell.get_instances()

        self.assertEqual(self.cell.cell.instances.ids, [])


if __name__ == '__main__':
    unittest.main()
