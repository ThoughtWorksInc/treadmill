"""Unit test for treadmill.appcfg
"""

import os
import shutil
import tempfile
import unittest

from treadmill import appcfg
from treadmill import fs


class AppCfgTest(unittest.TestCase):
    """Tests for teadmill.appcfg"""

    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        if self.root and os.path.isdir(self.root):
            shutil.rmtree(self.root)

    @staticmethod
    def _write_app_yaml(event, manifest_str):
        """Helper method to create app.yaml file in the event directory."""
        fs.mkdir_safe(os.path.dirname(event))
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(event),
                                         delete=False,
                                         mode='w') as f:
            f.write(manifest_str)
        os.rename(f.name, event)

    def test_gen_uniqueid(self):
        """Test generation of app uniqueid.
        """
        manifest = """
---
foo: bar
"""
        event_filename0 = os.path.join(self.root, 'proid.myapp#0')
        self._write_app_yaml(event_filename0, manifest)
        uniqueid1 = appcfg.gen_uniqueid(event_filename0)
        self._write_app_yaml(event_filename0, manifest)
        uniqueid2 = appcfg.gen_uniqueid(event_filename0)

        self.assertTrue(len(uniqueid1) <= 13)
        self.assertNotEquals(uniqueid1, uniqueid2)


if __name__ == '__main__':
    unittest.main()
