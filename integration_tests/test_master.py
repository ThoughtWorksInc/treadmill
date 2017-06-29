"""
Unit test for EC2 master setup.
"""

import unittest
from treadmill.infra.setup.master import Master
from treadmill.infra import constants


class MasterTest(unittest.TestCase):
    """Tests EC2 master setup."""

    def setUp(self):
        self.attempted_destroy = False
        self.master = Master(
            domain='ms.treadmill',
            app_root='/var/tmp'
        )

    def tearDown(self):
        if not self.attempted_destroy:
            self.master.destroy()

    def test_setup_master(self):
        self.vpc_id = self.master.setup(
            Name='TreadmillMaster',
            ImageId='ami-9e2f0988',
            Count=3,
            tm_release='0.1.0',
            freeipa_hostname='freeipa',
            KeyName='ms_treadmill_dev',
            InstanceType=constants.INSTANCE_TYPES['EC2']['small'],
        )
        output = self.master.output

        self.assertEquals(len(self.master.ids), 3)
        self.assertIsNotNone(self.vpc_id)
        self.assertIsNotNone(self.master.vpc.hosted_zone_id)
        self.assertEquals(output['VpcId'], self.vpc_id)
        self.assertEquals(len(output['Instances']), 3)
        for instance in output['Instances']:
            self.assertIsNotNone(instance['InstanceId'])
            self.assertIsNotNone(instance['SubnetId'])
            self.assertIsNotNone(instance['SecurityGroups'])
            self.assertIn(instance['InstanceState'], ['pending', 'running'])
            self.assertIn(instance['SubnetId'], self.master.vpc.subnet_ids)

        self.master.destroy()
        self.attempted_destroy = True

        self.master.vpc.instances = None
        self.master.vpc.instance_ids = None
        self.master.vpc.get_instances()

        self.assertIsNone(self.master.vpc.instance_ids, None)


if __name__ == '__main__':
    unittest.main()
