"""
Tests for the storage module.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from clipstack.storage import StorageManager, ClipboardItem


class TestClipboardItem:
    """Test cases for ClipboardItem class."""
    
    def test_init(self):
        """Test ClipboardItem initialization."""
        item = ClipboardItem(
            content="test content",
            timestamp=1234567890.0,
            content_type="text",
            content_length=12,
            lines=1,
            words=2
        )
        
        assert item.content == "test content"
        assert item.timestamp == 1234567890.0
        assert item.content_type == "text"
        assert item.content_length == 12
        assert item.lines == 1
        assert item.words == 2
    
    def test_from_dict(self):
        """Test creating ClipboardItem from dictionary."""
        data = {
            "content": "test content",
            "timestamp": 1234567890.0,
            "content_type": "text",
            "content_length": 12,
            "lines": 1,
            "words": 2
        }
        
        item = ClipboardItem.from_dict(data)
        
        assert item.content == "test content"
        assert item.timestamp == 1234567890.0
        assert item.content_type == "text"
        assert item.content_length == 12
        assert item.lines == 1
        assert item.words == 2
    
    def test_to_dict(self):
        """Test converting ClipboardItem to dictionary."""
        item = ClipboardItem(
            content="test content",
            timestamp=1234567890.0,
            content_type="text",
            content_length=12,
            lines=1,
            words=2
        )
        
        data = item.to_dict()
        
        assert data["content"] == "test content"
        assert data["timestamp"] == 1234567890.0
        assert data["content_type"] == "text"
        assert data["content_length"] == 12
        assert data["lines"] == 1
        assert data["words"] == 2
    
    def test_datetime_property(self):
        """Test datetime property."""
        from datetime import datetime
        
        item = ClipboardItem(
            content="test",
            timestamp=1234567890.0,
            content_type="text",
            content_length=4,
            lines=1,
            words=1
        )
        
        dt = item.datetime
        assert isinstance(dt, datetime)
        assert dt.timestamp() == 1234567890.0
    
    def test_formatted_timestamp(self):
        """Test formatted timestamp property."""
        item = ClipboardItem(
            content="test",
            timestamp=1234567890.0,
            content_type="text",
            content_length=4,
            lines=1,
            words=1
        )
        
        formatted = item.formatted_timestamp
        assert isinstance(formatted, str)
        assert "2009" in formatted  # 1234567890.0 corresponds to 2009


class TestStorageManager:
    """Test cases for StorageManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.storage_path = self.temp_file.name
        
        self.storage = StorageManager(storage_path=self.storage_path, max_history=5)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.storage_path):
            os.unlink(self.storage_path)
    
    def test_init_default(self):
        """Test StorageManager initialization with default values."""
        # Test with default path
        with patch('clipstack.storage.Path.home') as mock_home:
            mock_home.return_value = Path("/home/test")
            storage = StorageManager()
            
            assert storage.max_history == 200
            assert storage.storage_path == Path("/home/test/.clipstack.json")
            assert storage.history == []
    
    def test_init_custom(self):
        """Test StorageManager initialization with custom values."""
        assert self.storage.max_history == 5
        assert self.storage.storage_path == Path(self.storage_path)
        assert self.storage.history == []
    
    def test_add_item_success(self):
        """Test successful item addition."""
        result = self.storage.add_item("test content", "text")
        
        assert result is True
        assert len(self.storage.history) == 1
        assert self.storage.history[0].content == "test content"
        assert self.storage.history[0].content_type == "text"
    
    def test_add_item_empty_content(self):
        """Test adding empty content."""
        result = self.storage.add_item("", "text")
        assert result is False
        assert len(self.storage.history) == 0
    
    def test_add_item_whitespace_content(self):
        """Test adding whitespace-only content."""
        result = self.storage.add_item("   \n\t   ", "text")
        assert result is False
        assert len(self.storage.history) == 0
    
    def test_add_item_duplicate_consecutive(self):
        """Test adding duplicate consecutive items."""
        # Add first item
        self.storage.add_item("test content", "text")
        assert len(self.storage.history) == 1
        
        # Try to add same content again
        result = self.storage.add_item("test content", "text")
        assert result is False
        assert len(self.storage.history) == 1
    
    def test_add_item_max_history(self):
        """Test max history limit enforcement."""
        # Add items up to max history
        for i in range(6):  # More than max_history (5)
            self.storage.add_item(f"content {i}", "text")
        
        # Should only keep max_history items
        assert len(self.storage.history) == 5
        assert self.storage.history[0].content == "content 5"  # Most recent first
    
    def test_get_item_valid_index(self):
        """Test getting item with valid index."""
        self.storage.add_item("test content", "text")
        item = self.storage.get_item(0)
        
        assert item is not None
        assert item.content == "test content"
    
    def test_get_item_invalid_index(self):
        """Test getting item with invalid index."""
        item = self.storage.get_item(0)
        assert item is None
        
        item = self.storage.get_item(-1)
        assert item is None
    
    def test_get_latest(self):
        """Test getting latest item."""
        # No items
        latest = self.storage.get_latest()
        assert latest is None
        
        # Add items
        self.storage.add_item("first", "text")
        self.storage.add_item("second", "text")
        
        latest = self.storage.get_latest()
        assert latest.content == "second"  # Most recent first
    
    def test_remove_item_success(self):
        """Test successful item removal."""
        self.storage.add_item("test content", "text")
        assert len(self.storage.history) == 1
        
        result = self.storage.remove_item(0)
        assert result is True
        assert len(self.storage.history) == 0
    
    def test_remove_item_invalid_index(self):
        """Test removing item with invalid index."""
        result = self.storage.remove_item(0)
        assert result is False
    
    def test_clear_history(self):
        """Test clearing all history."""
        # Add some items
        self.storage.add_item("content 1", "text")
        self.storage.add_item("content 2", "text")
        assert len(self.storage.history) == 2
        
        # Clear history
        result = self.storage.clear_history()
        assert result is True
        assert len(self.storage.history) == 0
    
    def test_search_items(self):
        """Test searching items."""
        # Add test items
        self.storage.add_item("python code example", "code")
        self.storage.add_item("javascript function", "code")
        self.storage.add_item("random text", "text")
        
        # Search for "python"
        results = self.storage.search_items("python")
        assert len(results) == 1
        assert results[0].content == "python code example"
        
        # Search for "code"
        results = self.storage.search_items("code")
        assert len(results) == 2
        
        # Search with limit
        results = self.storage.search_items("code", limit=1)
        assert len(results) == 1
    
    def test_search_items_empty_query(self):
        """Test searching with empty query."""
        results = self.storage.search_items("")
        assert results == []
        
        results = self.storage.search_items("   ")
        assert results == []
    
    def test_get_history_stats_empty(self):
        """Test getting stats for empty history."""
        stats = self.storage.get_history_stats()
        
        assert stats['total_items'] == 0
        assert stats['oldest_item'] is None
        assert stats['newest_item'] is None
        assert stats['total_content_length'] == 0
        assert stats['content_types'] == {}
        assert stats['average_content_length'] == 0
    
    def test_get_history_stats_with_items(self):
        """Test getting stats for history with items."""
        # Add test items
        self.storage.add_item("short", "text")
        self.storage.add_item("longer content", "text")
        
        stats = self.storage.get_history_stats()
        
        assert stats['total_items'] == 2
        assert stats['total_content_length'] == 19  # 5 + 14
        assert stats['average_content_length'] == 9.5
        assert 'text' in stats['content_types']
        assert stats['content_types']['text'] == 2
    
    def test_save_and_load_history(self):
        """Test saving and loading history."""
        # Add test items
        self.storage.add_item("test content 1", "text")
        self.storage.add_item("test content 2", "code")
        
        # Create new storage manager to load from file
        new_storage = StorageManager(storage_path=self.storage_path, max_history=5)
        
        assert len(new_storage.history) == 2
        assert new_storage.history[0].content == "test content 2"  # Most recent first
        assert new_storage.history[1].content == "test content 1"
    
    def test_export_history_json(self):
        """Test exporting history to JSON."""
        # Add test items
        self.storage.add_item("test content", "text")
        
        # Export to temporary file
        export_path = self.storage_path + ".export"
        result = self.storage.export_history(export_path, "json")
        
        assert result is True
        assert os.path.exists(export_path)
        
        # Verify exported content
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == 1
        assert exported_data[0]['content'] == "test content"
        
        # Clean up
        os.unlink(export_path)
    
    def test_export_history_csv(self):
        """Test exporting history to CSV."""
        # Add test items
        self.storage.add_item("test content", "text")
        
        # Export to temporary file
        export_path = self.storage_path + ".export.csv"
        result = self.storage.export_history(export_path, "csv")
        
        assert result is True
        assert os.path.exists(export_path)
        
        # Clean up
        os.unlink(export_path)
    
    def test_export_history_unsupported_format(self):
        """Test exporting with unsupported format."""
        result = self.storage.export_history("test.txt", "txt")
        assert result is False
    
    def test_import_history_json(self):
        """Test importing history from JSON."""
        # Create test export data
        test_data = [
            {
                "content": "imported content 1",
                "timestamp": 1234567890.0,
                "content_type": "text",
                "content_length": 20,
                "lines": 1,
                "words": 3
            },
            {
                "content": "imported content 2",
                "timestamp": 1234567891.0,
                "content_type": "code",
                "content_length": 20,
                "lines": 1,
                "words": 3
            }
        ]
        
        # Write test data to file
        with open(self.storage_path + ".import", 'w') as f:
            json.dump(test_data, f)
        
        # Import
        result = self.storage.import_history(self.storage_path + ".import", "json")
        assert result is True
        assert len(self.storage.history) == 2
        
        # Clean up
        os.unlink(self.storage_path + ".import")
    
    def test_import_history_merge(self):
        """Test importing history with merge option."""
        # Add existing item
        self.storage.add_item("existing content", "text")
        
        # Create test import data
        test_data = [
            {
                "content": "imported content",
                "timestamp": 1234567890.0,
                "content_type": "text",
                "content_length": 18,
                "lines": 1,
                "words": 2
            }
        ]
        
        # Write test data to file
        with open(self.storage_path + ".import", 'w') as f:
            json.dump(test_data, f)
        
        # Import with merge
        result = self.storage.import_history(self.storage_path + ".import", "json", merge=True)
        assert result is True
        assert len(self.storage.history) == 2  # Existing + imported
        
        # Clean up
        os.unlink(self.storage_path + ".import")
    
    def test_import_history_replace(self):
        """Test importing history with replace option."""
        # Add existing item
        self.storage.add_item("existing content", "text")
        
        # Create test import data
        test_data = [
            {
                "content": "imported content",
                "timestamp": 1234567890.0,
                "content_type": "text",
                "content_length": 18,
                "lines": 1,
                "words": 2
            }
        ]
        
        # Write test data to file
        with open(self.storage_path + ".import", 'w') as f:
            json.dump(test_data, f)
        
        # Import with replace
        result = self.storage.import_history(self.storage_path + ".import", "json", merge=False)
        assert result is True
        assert len(self.storage.history) == 1  # Only imported
        
        # Clean up
        os.unlink(self.storage_path + ".import")
    
    def test_get_storage_info(self):
        """Test getting storage information."""
        info = self.storage.get_storage_info()
        
        assert info['storage_path'] == self.storage_path
        # Check that storage_exists reflects the actual state
        assert info['storage_exists'] == os.path.exists(self.storage_path)
        assert info['max_history'] == 5
        # current_history_size should match the actual history length
        assert info['current_history_size'] == len(self.storage.history)
        assert info['storage_format'] == "json"
