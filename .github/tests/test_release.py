import unittest
import os
import shutil
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to import the module code. Since it's in a .scripts folder which isn't a package,
# we might need to load it dynamically or just rely on the sys.path append above 
# and the fact that we can import from .scripts if we were in root, but .scripts is hidden.
# Easier approach: Load source file directly.

import importlib.util
spec = importlib.util.spec_from_file_location("release", ".github/scripts/release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

class TestReleaseScript(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.version_file = 'VERSION'
        with open(self.version_file, 'w') as f:
            f.write('1.2.3')

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_bump_patch(self):
        new_ver = release.bump_version('1.2.3', 'patch')
        self.assertEqual(new_ver, '1.2.4')

    def test_bump_minor(self):
        new_ver = release.bump_version('1.2.3', 'minor')
        self.assertEqual(new_ver, '1.3.0')

    def test_bump_major(self):
        new_ver = release.bump_version('1.2.3', 'major')
        self.assertEqual(new_ver, '2.0.0')

    @patch('os.getcwd')
    def test_reset_allowed_in_scaffolding_repo(self, mock_getcwd):
        mock_getcwd.return_value = '/home/user/code/github_scaffolding'
        self.assertTrue(release.is_safe_to_reset())

    @patch('os.getcwd')
    def test_reset_forbidden_elsewhere(self, mock_getcwd):
        mock_getcwd.return_value = '/home/user/code/other_project'
        self.assertFalse(release.is_safe_to_reset())

    def test_write_version(self):
        release.write_version('9.9.9')
        with open(self.version_file, 'r') as f:
            content = f.read().strip()
        self.assertEqual(content, '9.9.9')

if __name__ == '__main__':
    unittest.main()
