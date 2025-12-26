"""Tests for the version info context processor."""
import os
from unittest.mock import Mock, patch, mock_open
import pytest
from web.context_processors import (
    version_info,
    get_git_commit,
    get_repo_url,
)


class TestVersionInfoContextProcessor:
    """Test the version info context processor."""

    def test_version_info_returns_dict(self):
        """Test that version_info returns a dictionary with expected keys."""
        request = Mock()
        context = version_info(request)

        assert isinstance(context, dict)
        assert 'git_commit' in context
        assert 'repo_url' in context

    @patch('web.context_processors.subprocess.check_output')
    def test_get_git_commit_success(self, mock_subprocess):
        """Test getting git commit hash successfully."""
        mock_subprocess.return_value = b'abc1234\n'
        result = get_git_commit()
        assert result == 'abc1234'

    @patch('web.context_processors.subprocess.check_output')
    def test_get_git_commit_failure(self, mock_subprocess):
        """Test git commit hash fallback on error."""
        mock_subprocess.side_effect = FileNotFoundError()
        result = get_git_commit()
        assert result == 'unknown'

    @patch('web.context_processors.subprocess.check_output')
    def test_get_repo_url_success(self, mock_subprocess):
        """Test getting repo url successfully."""
        mock_subprocess.return_value = b'https://github.com/example/repo.git\n'
        result = get_repo_url()
        assert result == 'https://github.com/example/repo.git'

    @patch('web.context_processors.subprocess.check_output')
    def test_get_repo_url_failure(self, mock_subprocess):
        """Test repo url fallback on error."""
        mock_subprocess.side_effect = FileNotFoundError()
        result = get_repo_url()
        assert result == ''

    def test_get_git_commit_env_var(self):
        """Test getting git commit from environment variable."""
        with patch.dict(os.environ, {'GIT_COMMIT': 'env_commit_hash'}):
            result = get_git_commit()
            assert result == 'env_commit_hash'

    def test_get_repo_url_env_var(self):
        """Test getting repo url from environment variable."""
        with patch.dict(os.environ, {'REPO_URL': 'https://env.example.com/repo'}):
            result = get_repo_url()
            assert result == 'https://env.example.com/repo'

    @patch('web.context_processors.subprocess.check_output')
    def test_get_repo_url_ssh_conversion(self, mock_subprocess):
        """Test converting SSH git URL to HTTPS."""
        mock_subprocess.return_value = b'git@github.com:owner/repo.git\n'
        result = get_repo_url()
        assert result == 'https://github.com/owner/repo'
