"""
Integration test for EC2 ipa setup.
"""

import unittest
from treadmill.infra.setup.cell import Cell
from treadmill.infra.setup.ipa import IPA
from treadmill.infra import constants


class IPATest(unittest.TestCase):
    """Tests EC2 cell setup."""

    def setUp(self):
        self.cell = Cell(domain='ms.treadmill')

    def tearDown(self):
        self.cell.vpc.delete()

    def test_setup_cell(self):
        self.cell.setup_vpc(
            vpc_cidr_block='172.23.0.0/16',
            secgroup_name='sg_common',
            secgroup_desc='Treadmill CIDR block'
        )
        self.ipa = IPA(
            domain='ms.treadmill',
            vpc_id=self.cell.vpc.id,
            name='treadmill-ipa'
        )
        self.ipa.setup(
            image_id='ami-9e2f0988',
            count=1,
            tm_release='0.1.1.rc1',
            key='ms_treadmill_dev',
            instance_type=constants.INSTANCE_TYPES['EC2']['medium'],
            ipa_admin_password='password',
            cidr_block='172.23.0.0/24'
        )
        output = self.ipa.subnet.show()

        self.assertIsNotNone(self.cell.vpc.hosted_zone_id)
        self.assertIsNotNone(self.cell.vpc.reverse_hosted_zone_id)
        self.assertEquals(output['VpcId'], self.ipa.vpc.id)
        self.assertEquals(len(output['Instances']), 1)
        for instance in output['Instances']:
            self.assertIsNotNone(instance['InstanceId'])
            self.assertIsNotNone(instance['SubnetId'])
            self.assertIsNotNone(instance['SecurityGroups'])
            self.assertIn(instance['InstanceState'], ['pending', 'running'])
            self.assertIn(instance['SubnetId'], self.ipa.subnet.id)

        self.ipa.destroy(subnet_id=self.ipa.subnet.id)

        self.ipa.subnet.instances = None
        self.ipa.subnet.get_instances()

        self.assertEqual(self.ipa.subnet.instances.ids, [])


if __name__ == '__main__':
    unittest.main()
