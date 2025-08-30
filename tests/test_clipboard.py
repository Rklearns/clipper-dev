"""
Tests for the clipboard module.
"""

import pytest
from unittest.mock import patch, MagicMock
from clipstack.clipboard import ClipboardManager


class TestClipboardManager:
    """Test cases for ClipboardManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.clipboard = ClipboardManager()
    
    def test_init(self):
        """Test ClipboardManager initialization."""
        assert self.clipboard.auto_track is True
        assert self.clipboard.track_interval == 1.0
        assert self.clipboard.last_content is None
        assert self.clipboard.monitoring is False
    
    @patch('clipstack.clipboard.pyperclip.paste')
    def test_get_content_success(self, mock_paste):
        """Test successful clipboard content retrieval."""
        mock_paste.return_value = "test content"
        content = self.clipboard.get_content()
        assert content == "test content"
    
    @patch('clipstack.clipboard.pyperclip.paste')
    def test_get_content_empty(self, mock_paste):
        """Test clipboard content retrieval when empty."""
        mock_paste.return_value = ""
        content = self.clipboard.get_content()
        assert content == ""
    
    @patch('clipstack.clipboard.pyperclip.paste')
    def test_get_content_exception(self, mock_paste):
        """Test clipboard content retrieval with exception."""
        from pyperclip import PyperclipException
        mock_paste.side_effect = PyperclipException("Clipboard error")
        
        with patch('clipstack.clipboard.console') as mock_console:
            content = self.clipboard.get_content()
            assert content == ""
            mock_console.print.assert_called_once()
    
    @patch('clipstack.clipboard.pyperclip.copy')
    def test_set_content_success(self, mock_copy):
        """Test successful clipboard content setting."""
        result = self.clipboard.set_content("new content")
        assert result is True
        assert self.clipboard.last_content == "new content"
        mock_copy.assert_called_once_with("new content")
    
    @patch('clipstack.clipboard.pyperclip.copy')
    def test_set_content_exception(self, mock_copy):
        """Test clipboard content setting with exception."""
        from pyperclip import PyperclipException
        mock_copy.side_effect = PyperclipException("Clipboard error")
        
        with patch('clipstack.clipboard.console') as mock_console:
            result = self.clipboard.set_content("new content")
            assert result is False
            mock_console.print.assert_called_once()
    
    @patch('clipstack.clipboard.pyperclip.paste')
    def test_has_changed_true(self, mock_paste):
        """Test clipboard change detection when content has changed."""
        mock_paste.return_value = "new content"
        self.clipboard.last_content = "old content"
        
        result = self.clipboard.has_changed()
        assert result is True
        assert self.clipboard.last_content == "new content"
    
    @patch('clipstack.clipboard.pyperclip.paste')
    def test_has_changed_false(self, mock_paste):
        """Test clipboard change detection when content hasn't changed."""
        mock_paste.return_value = "same content"
        self.clipboard.last_content = "same content"
        
        result = self.clipboard.has_changed()
        assert result is False
    
    @patch('clipstack.clipboard.pyperclip.paste')
    def test_get_content_info(self, mock_paste):
        """Test content info retrieval."""
        mock_paste.return_value = "test\ncontent\nhere"
        
        with patch('clipstack.clipboard.time.time') as mock_time:
            mock_time.return_value = 1234567890.0
            info = self.clipboard.get_content_info()
            
            assert info['content'] == "test\ncontent\nhere"
            assert info['length'] == 17
            assert info['lines'] == 3
            assert info['words'] == 3
            assert info['is_empty'] is False
            assert info['timestamp'] == 1234567890.0
    
    def test_validate_content_valid(self):
        """Test content validation with valid content."""
        assert self.clipboard.validate_content("valid content") is True
        assert self.clipboard.validate_content("") is True
    
    def test_validate_content_invalid_type(self):
        """Test content validation with invalid type."""
        assert self.clipboard.validate_content(123) is False
        assert self.clipboard.validate_content(None) is False
    
    def test_validate_content_too_large(self):
        """Test content validation with content that's too large."""
        large_content = "x" * (10 * 1024 * 1024 + 1)  # Just over 10MB
        assert self.clipboard.validate_content(large_content) is False
    
    def test_format_content_preview_short(self):
        """Test content preview formatting with short content."""
        preview = self.clipboard.format_content_preview("short content", 20)
        assert preview == "short content"
    
    def test_format_content_preview_long(self):
        """Test content preview formatting with long content."""
        long_content = "this is a very long content that exceeds the preview length"
        preview = self.clipboard.format_content_preview(long_content, 20)
        assert preview == "this is a very lo..."
    
    def test_format_content_preview_empty(self):
        """Test content preview formatting with empty content."""
        preview = self.clipboard.format_content_preview("", 20)
        assert preview == "[empty]"
    
    def test_get_clipboard_type_url(self):
        """Test clipboard type detection for URLs."""
        assert self.clipboard.get_clipboard_type("https://example.com") == "url"
        assert self.clipboard.get_clipboard_type("http://test.org") == "url"
    
    def test_get_clipboard_type_email(self):
        """Test clipboard type detection for emails."""
        assert self.clipboard.get_clipboard_type("user@example.com") == "email"
    
    def test_get_clipboard_type_short_text(self):
        """Test clipboard type detection for short text."""
        assert self.clipboard.get_clipboard_type("short") == "short_text"
    
    def test_get_clipboard_type_long_text(self):
        """Test clipboard type detection for long text."""
        long_text = "this is a very long text that exceeds the short text threshold"
        assert self.clipboard.get_clipboard_type(long_text) == "long_text"
    
    def test_get_clipboard_type_code(self):
        """Test clipboard type detection for code."""
        code = "# This is a comment\nprint('Hello World')"
        assert self.clipboard.get_clipboard_type(code) == "code"
    
    def test_get_clipboard_type_multi_line(self):
        """Test clipboard type detection for multi-line text."""
        multi_line = "line 1\nline 2\nline 3"
        assert self.clipboard.get_clipboard_type(multi_line) == "multi_line_text"
    
    def test_get_clipboard_type_empty(self):
        """Test clipboard type detection for empty content."""
        assert self.clipboard.get_clipboard_type("") == "empty"
    
    def test_get_status(self):
        """Test status information retrieval."""
        with patch('clipstack.clipboard.pyperclip.determine_clipboard') as mock_determine:
            mock_determine.return_value = "test_platform"
            
            status = self.clipboard.get_status()
            
            assert status['auto_track'] is True
            assert status['track_interval'] == 1.0
            assert status['monitoring'] is False
            assert status['last_content_length'] == 0
            assert status['platform'] == "test_platform"
    
    def test_is_monitoring(self):
        """Test monitoring status check."""
        assert self.clipboard.is_monitoring() is False
        
        self.clipboard.monitoring = True
        assert self.clipboard.is_monitoring() is True
