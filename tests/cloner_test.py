import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import logging

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.cloner import GitCloner


class TestGitCloner(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cloner = GitCloner()
        self.test_repo_url = "https://github.com/octocat/Hello-World.git"
        self.test_target_dir = os.path.join(self.temp_dir, "test_repo")
        
    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_with_logger(self):
        logger = logging.getLogger("test_logger")
        cloner = GitCloner(logger)
        self.assertEqual(cloner.logger, logger)
    
    def test_init_without_logger(self):
        cloner = GitCloner()
        self.assertIsNotNone(cloner.logger)
        self.assertEqual(cloner.logger.name, "tools.cloner")
    
    @patch('subprocess.run')
    def test_clone_repository_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Cloning successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.cloner.clone_repository(self.test_repo_url, self.test_target_dir)
        
        expected_path = str(Path(self.test_target_dir).absolute())
        self.assertEqual(result, expected_path)
        mock_run.assert_called_once_with(
            ['git', 'clone', self.test_repo_url, self.test_target_dir],
            capture_output=True, text=True, check=True
        )
    
    @patch('subprocess.run')
    def test_clone_repository_with_branch(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Cloning successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.cloner.clone_repository(self.test_repo_url, self.test_target_dir, "main")
        
        expected_path = str(Path(self.test_target_dir).absolute())
        self.assertEqual(result, expected_path)
        mock_run.assert_called_once_with(
            ['git', 'clone', self.test_repo_url, self.test_target_dir, '--branch', 'main'],
            capture_output=True, text=True, check=True
        )
    
    def test_clone_repository_empty_url(self):
        with self.assertRaises(ValueError) as context:
            self.cloner.clone_repository("", self.test_target_dir)
        self.assertIn("Repository URL cannot be empty", str(context.exception))
    
    def test_clone_repository_empty_target_dir(self):
        with self.assertRaises(ValueError) as context:
            self.cloner.clone_repository(self.test_repo_url, "")
        self.assertIn("Target directory cannot be empty", str(context.exception))
    
    @patch('subprocess.run')
    def test_clone_repository_git_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(128, ['git', 'clone'], "", "fatal: repository 'https://invalid-url.git' does not exist")
        
        with self.assertRaises(RuntimeError) as context:
            self.cloner.clone_repository("https://invalid-url.git", self.test_target_dir)
        self.assertIn("Git clone failed", str(context.exception))
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    @patch('tools.cloner.GitCloner._delete_directory')
    @patch('subprocess.run')
    def test_clone_repository_existing_dir(self, mock_run, mock_delete, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Cloning successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.cloner.clone_repository(self.test_repo_url, self.test_target_dir)
        
        mock_delete.assert_called_once()
        self.assertTrue(result)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_clone_repository_existing_file(self, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = False
        
        with self.assertRaises(ValueError) as context:
            self.cloner.clone_repository(self.test_repo_url, self.test_target_dir)
        self.assertIn("exists but is not a directory", str(context.exception))
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    @patch('tools.cloner.GitCloner._delete_directory')
    def test_delete_repository_success(self, mock_delete, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = True
        result = self.cloner.delete_repository(self.test_target_dir)
        self.assertTrue(result)
        mock_delete.assert_called_once()
    
    def test_delete_repository_empty_path(self):
        with self.assertRaises(ValueError) as context:
            self.cloner.delete_repository("")
        self.assertIn("Repository path cannot be empty", str(context.exception))
    
    @patch('pathlib.Path.exists')
    def test_delete_repository_nonexistent_path(self, mock_exists):
        mock_exists.return_value = False
        
        result = self.cloner.delete_repository("/nonexistent/path")
        self.assertTrue(result)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_delete_repository_not_directory(self, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = False
        
        with self.assertRaises(ValueError) as context:
            self.cloner.delete_repository(self.test_target_dir)
        self.assertIn("is not a directory", str(context.exception))
    
    def test_delete_directory_recursive(self):
        test_dir = os.path.join(self.temp_dir, "recursive_test")
        os.makedirs(test_dir)
        
        subdir = os.path.join(test_dir, "subdir")
        os.makedirs(subdir)
        
        test_file = os.path.join(subdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        self.assertTrue(os.path.exists(test_dir))
        self.cloner._delete_directory(Path(test_dir))
        self.assertFalse(os.path.exists(test_dir))
    
    def test_delete_directory_file(self):
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        self.assertTrue(os.path.exists(test_file))
        self.cloner._delete_directory(Path(test_file))
        self.assertFalse(os.path.exists(test_file))
    
    @patch('subprocess.run')
    def test_get_repo_info_success(self, mock_run):
        os.makedirs(self.test_target_dir)
        os.makedirs(os.path.join(self.test_target_dir, '.git'))
        
        def mock_subprocess_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            if 'remote.origin.url' in cmd:
                result.stdout = self.test_repo_url
            elif '--show-current' in cmd:
                result.stdout = "main"
            elif 'rev-parse' in cmd:
                result.stdout = "abc123def456"
            return result
        
        mock_run.side_effect = mock_subprocess_run
        
        result = self.cloner.get_repo_info(self.test_target_dir)
        
        expected = {
            'remote_url': self.test_repo_url,
            'current_branch': 'main',
            'commit_hash': 'abc123def456',
            'path': str(Path(self.test_target_dir).absolute())
        }
        
        self.assertEqual(result, expected)
        self.assertEqual(mock_run.call_count, 3)
    
    def test_get_repo_info_empty_path(self):
        with self.assertRaises(ValueError) as context:
            self.cloner.get_repo_info("")
        self.assertIn("Repository path cannot be empty", str(context.exception))
    
    def test_get_repo_info_nonexistent_path(self):
        with self.assertRaises(ValueError) as context:
            self.cloner.get_repo_info("/nonexistent/path")
        self.assertIn("does not exist", str(context.exception))
    
    def test_get_repo_info_not_git_repo(self):
        os.makedirs(self.test_target_dir)
        
        with self.assertRaises(ValueError) as context:
            self.cloner.get_repo_info(self.test_target_dir)
        self.assertIn("is not a git repository", str(context.exception))
    
    @patch('subprocess.run')
    def test_get_repo_info_git_error(self, mock_run):
        os.makedirs(self.test_target_dir)
        os.makedirs(os.path.join(self.test_target_dir, '.git'))
        
        mock_run.side_effect = subprocess.CalledProcessError(128, ['git', 'config'], "", "fatal: not a git repository")
        
        with self.assertRaises(RuntimeError) as context:
            self.cloner.get_repo_info(self.test_target_dir)
        self.assertIn("Failed to get repository info", str(context.exception))
    
    @patch('pathlib.Path.exists')
    @patch('subprocess.run')
    def test_permission_error_handling(self, mock_run, mock_exists):
        mock_exists.return_value = False
        mock_run.side_effect = PermissionError("Permission denied")
        
        with self.assertRaises(RuntimeError) as context:
            self.cloner.clone_repository(self.test_repo_url, self.test_target_dir)
        self.assertIn("Permission denied", str(context.exception))


if __name__ == '__main__':
    unittest.main()