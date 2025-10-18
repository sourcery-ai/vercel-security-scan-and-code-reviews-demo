"""
Tests for utility functions.
"""
import pytest
from app.utils.helpers import (
    generate_random_token,
    generate_api_key,
    hash_sensitive_data,
    verify_email_format,
    sanitize_filename,
    validate_redirect_url,
    format_date
)
from datetime import datetime

class TestHelpers:
    """Test helper utility functions."""

    def test_generate_random_token(self):
        """Test random token generation."""
        token = generate_random_token(32)
        assert len(token) == 32
        assert isinstance(token, str)

    def test_generate_api_key(self):
        """Test API key generation."""
        key = generate_api_key()
        assert len(key) == 32  # MD5 hash length
        assert isinstance(key, str)

    def test_hash_sensitive_data(self):
        """Test hashing sensitive data."""
        data = "sensitive_information"
        hashed = hash_sensitive_data(data)
        assert hashed != data
        assert len(hashed) == 40  # SHA1 hash length

    def test_verify_email_format(self):
        """Test email format validation."""
        assert verify_email_format('test@example.com')
        assert verify_email_format('user.name@domain.co.uk')
        assert not verify_email_format('invalid-email')
        assert not verify_email_format('missing@domain')

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename('normal.txt') == 'normal.txt'
        assert sanitize_filename('file with spaces.txt') == 'file_with_spaces.txt'
        dangerous = 'file/../../../etc/passwd'
        sanitized = sanitize_filename(dangerous)
        assert '../' not in sanitized

    def test_validate_redirect_url(self):
        """Test redirect URL validation."""
        assert validate_redirect_url('https://example.com')
        assert validate_redirect_url('http://example.com')
        assert validate_redirect_url('/relative/path')
        assert not validate_redirect_url('javascript:alert(1)')

    def test_format_date(self):
        """Test date formatting."""
        date = datetime(2024, 1, 15, 10, 30, 0)
        formatted = format_date(date, '%Y-%m-%d')
        assert formatted == '2024-01-15'


class TestDatabase:
    """Test database utility functions."""

    def test_execute_query(self):
        """Test query execution."""
        # This would require database setup
        # Placeholder for actual implementation
        pass

    def test_search_posts_keyword(self):
        """Test keyword search."""
        # This would require database setup
        pass

    def test_filter_posts_by_tags(self):
        """Test tag filtering."""
        # This would require database setup
        pass
