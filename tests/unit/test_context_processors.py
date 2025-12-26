"""Tests for the version info context processor."""
import os
from unittest.mock import Mock, patch, mock_open
import pytest
from web.context_processors import (
    version_info,
    get_git_commit,
    get_app_version,
    get_docker_hash,
)


class TestVersionInfoContextProcessor:
    """Test the version info context processor."""

    def test_version_info_returns_dict(self):
        """Test that version_info returns a dictionary with expected keys."""
        request = Mock()
        context = version_info(request)

        assert isinstance(context, dict)
        assert 'git_commit' in context
        assert 'app_version' in context
        assert 'docker_hash' in context

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
    def test_get_app_version_from_git_tag(self, mock_subprocess):
        """Test getting app version from git tag."""
        mock_subprocess.return_value = b'v1.2.3\n'
        result = get_app_version()
        assert result == 'v1.2.3'

    @patch('web.context_processors.subprocess.check_output')
    def test_get_app_version_fallback_to_pyproject(self, mock_subprocess):
        """Test getting app version from pyproject.toml when git tag fails."""
        mock_subprocess.side_effect = FileNotFoundError()

        # The actual implementation uses tomli.load, so we need to patch it correctly
        with patch('tomli.load') as mock_tomli:
            mock_tomli.return_value = {'project': {'version': '0.2.2'}}
            with patch('builtins.open', mock_open(read_data=b'[project]\nversion = "0.2.2"')):
                result = get_app_version()
                assert result == '0.2.2'

    @patch('web.context_processors.subprocess.check_output')
    def test_get_app_version_default_fallback(self, mock_subprocess):
        """Test default version fallback when all methods fail."""
        mock_subprocess.side_effect = FileNotFoundError()

        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = get_app_version()
            assert result == 'v0.0.0'

    @patch.dict(os.environ, {'HOSTNAME': 'abc123def456ghi'}, clear=False)
    def test_get_docker_hash_from_env(self):
        """Test getting docker hash from HOSTNAME environment variable."""
        result = get_docker_hash()
        assert result == 'abc123def456'  # Should be truncated to 12 chars

    @patch.dict(os.environ, {}, clear=True)
    @patch('builtins.open', mock_open(read_data='container123456789'))
    def test_get_docker_hash_from_hostname_file(self):
        """Test getting docker hash from /etc/hostname."""
        result = get_docker_hash()
        assert result == 'container123'  # Should be truncated to 12 chars

    @patch.dict(os.environ, {}, clear=True)
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_get_docker_hash_not_in_container(self, mock_file):
        """Test docker hash when not in a container."""
        result = get_docker_hash()
        assert result == 'not-in-container'

    @patch.dict(os.environ, {'HOSTNAME': 'short'}, clear=False)
    @patch('builtins.open', mock_open(read_data='container123456789'))
    def test_get_docker_hash_short_hostname_fallback(self):
        """Test docker hash falls back to /etc/hostname when HOSTNAME is too short."""
        result = get_docker_hash()
        assert result == 'container123'  # Should use /etc/hostname instead
