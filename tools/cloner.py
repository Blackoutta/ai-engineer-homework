import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import logging

class GitCloner:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
    def clone_repository(self, repo_url: str, target_dir: str, branch: Optional[str] = None, author: Optional[str] = None) -> str:
        if not repo_url:
            raise ValueError("Repository URL cannot be empty")
        
        if not target_dir:
            raise ValueError("Target directory cannot be empty")
        
        target_path = Path(target_dir)
        
        if target_path.exists():
            if target_path.is_dir():
                self.logger.warning(f"Target directory {target_dir} already exists. Removing it.")
                self._delete_directory(target_path)
            else:
                raise ValueError(f"Target path {target_dir} exists but is not a directory")
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = ['git', 'clone', repo_url, str(target_path)]
        
        if branch:
            cmd.extend(['--branch', branch])
        
        log_message = f"Cloning repository {repo_url} to {target_dir}"
        if author:
            log_message += f" (author: {author})"
        self.logger.info(log_message)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr if e.stderr else "Unknown error"
            error_msg = f"Git clone failed: {stderr.strip()}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except PermissionError as e:
            error_msg = f"Permission denied when cloning repository: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        
        self.logger.info(f"Successfully cloned repository to {target_dir}")
        return str(target_path.absolute())
    
    def delete_repository(self, repo_path: str) -> bool:
        if not repo_path:
            raise ValueError("Repository path cannot be empty")
        
        path = Path(repo_path)
        
        if not path.exists():
            self.logger.warning(f"Repository path {repo_path} does not exist")
            return True
        
        if not path.is_dir():
            raise ValueError(f"Path {repo_path} is not a directory")
        
        try:
            self._delete_directory(path)
            self.logger.info(f"Successfully deleted repository at {repo_path}")
            return True
        except PermissionError as e:
            error_msg = f"Permission denied when deleting repository: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _delete_directory(self, path: Path) -> None:
        try:
            if path.is_dir():
                for item in path.iterdir():
                    if item.is_dir():
                        self._delete_directory(item)
                    else:
                        item.unlink()
                path.rmdir()
            else:
                path.unlink()
        except PermissionError as e:
            self.logger.error(f"Permission denied when deleting {path}: {str(e)}")
            raise
        except OSError as e:
            self.logger.error(f"OS error when deleting {path}: {str(e)}")
            raise
    
    def get_repo_info(self, repo_path: str) -> dict:
        if not repo_path:
            raise ValueError("Repository path cannot be empty")
        
        path = Path(repo_path)
        
        if not path.exists():
            raise ValueError(f"Repository path {repo_path} does not exist")
        
        if not (path / '.git').exists():
            raise ValueError(f"Path {repo_path} is not a git repository")
        
        original_cwd = os.getcwd()
        try:
            os.chdir(repo_path)
            
            try:
                remote_url_result = subprocess.run(
                    ['git', 'config', '--get', 'remote.origin.url'],
                    capture_output=True, text=True, check=True
                )
                remote_url = remote_url_result.stdout.strip()
                
                current_branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True, text=True, check=True
                )
                current_branch = current_branch_result.stdout.strip()
                
                commit_hash_result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    capture_output=True, text=True, check=True
                )
                commit_hash = commit_hash_result.stdout.strip()
                
                return {
                    'remote_url': remote_url,
                    'current_branch': current_branch,
                    'commit_hash': commit_hash,
                    'path': str(path.absolute())
                }
                
            except subprocess.CalledProcessError as e:
                stderr = e.stderr if e.stderr else "Unknown error"
                error_msg = f"Failed to get repository info: {stderr.strip()}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg) from e
                
        finally:
            os.chdir(original_cwd)