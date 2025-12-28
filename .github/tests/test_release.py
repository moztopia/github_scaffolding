import unittest
import os
import shutil
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import the script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        self.changelog_file = 'CHANGELOG.md'
        with open(self.version_file, 'w') as f:
            f.write('1.2.3')
        with open(self.changelog_file, 'w') as f:
            f.write('# Changelog\n\n')

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
    
    def test_parse_commits(self):
        commits = [
            'feat: new feature',
            'fix: bug fix',
            'docs: readme update',
            'chore: cleanup',
            'random commit'
        ]
        categories = release.parse_commits(commits)
        self.assertIn('feat: new feature', categories['Features'])
        self.assertIn('fix: bug fix', categories['Fixes'])
        self.assertIn('docs: readme update', categories['Docs'])
        self.assertIn('chore: cleanup', categories['Chores'])
        self.assertIn('random commit', categories['Other'])

    def test_generate_changelog_content(self):
        categories = {
            'Features': ['feat: Cool stuff'],
            'Fixes': [],
            'Docs': [],
            'Chores': [],
            'Other': []
        }
        content = release.generate_changelog_content('1.3.0', categories)
        self.assertIn('## [1.3.0]', content)
        self.assertIn('### Features', content)
        self.assertIn('- feat: Cool stuff', content)

    # Simplified test for update logic
    def test_update_changelog_file(self):
        content = "## [1.3.0] - 2023-10-27\n### Features\n- New thing\n"
        release.update_changelog_file(content)
        with open(self.changelog_file, 'r') as f:
            full_content = f.read()
        self.assertIn("## [1.3.0]", full_content)
        self.assertIn("New thing", full_content)

if __name__ == '__main__':
    unittest.main()
