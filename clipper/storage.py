"""
Storage management functionality for Clipper.

This module handles all data persistence operations including saving,
loading, and managing clipboard history with support for JSON storage
and future SQLite integration.
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class ClipboardItem:
    """Represents a single clipboard item with metadata."""

    content: str
    timestamp: float
    content_type: str
    content_length: int
    lines: int
    words: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClipboardItem":
        """Create a ClipboardItem from a dictionary."""
        return cls(
            content=data.get("content", ""),
            timestamp=data.get("timestamp", time.time()),
            content_type=data.get("content_type", "text"),
            content_length=data.get("content_length", 0),
            lines=data.get("lines", 0),
            words=data.get("words", 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ClipboardItem to dictionary."""
        return asdict(self)

    @property
    def datetime(self) -> datetime:
        """Get the timestamp as a datetime object."""
        return datetime.fromtimestamp(self.timestamp)

    @property
    def formatted_timestamp(self) -> str:
        """Get a formatted timestamp string."""
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")


class StorageManager:
    """
    Manages clipboard history storage and retrieval.

    This class provides a unified interface for storing and retrieving
    clipboard history with support for different storage backends.
    """

    def __init__(self, storage_path: Optional[str] = None, max_history: int = 200):
        """
        Initialize the storage manager.

        Args:
            storage_path: Path to the storage file
            max_history: Maximum number of items to keep in history
        """
        self.max_history = max_history

        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path.home() / ".clipper.json"

        self.history: List[ClipboardItem] = []
        self.load_history()

    def add_item(self, content: str, content_type: str = "text") -> bool:
        """
        Add a new item to the clipboard history.

        Args:
            content: The clipboard content to store
            content_type: Type of content (text, code, url, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Don't add empty content
            if not content.strip():
                return False

            # Don't add duplicate consecutive items
            if self.history and self.history[0].content == content:
                return False

            # Create new item
            item = ClipboardItem(
                content=content,
                timestamp=time.time(),
                content_type=content_type,
                content_length=len(content),
                lines=len(content.splitlines()),
                words=len(content.split()),
            )

            # Add to beginning of list (most recent first)
            self.history.insert(0, item)

            # Maintain max history size
            if len(self.history) > self.max_history:
                self.history = self.history[: self.max_history]

            # Save to disk
            self.save_history()
            return True

        except Exception as e:
            console.print(f"[red]Error adding item to history: {e}[/red]")
            return False

    def get_item(self, index: int) -> Optional[ClipboardItem]:
        """
        Get an item by index.

        Args:
            index: Index of the item to retrieve

        Returns:
            ClipboardItem if found, None otherwise
        """
        try:
            if 0 <= index < len(self.history):
                return self.history[index]
            return None
        except IndexError:
            return None

    def get_latest(self) -> Optional[ClipboardItem]:
        """
        Get the most recent clipboard item.

        Returns:
            Most recent ClipboardItem, or None if history is empty
        """
        return self.history[0] if self.history else None

    def remove_item(self, index: int) -> bool:
        """
        Remove an item by index.

        Args:
            index: Index of the item to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            if 0 <= index < len(self.history):
                del self.history[index]
                self.save_history()
                return True
            return False
        except Exception as e:
            console.print(f"[red]Error removing item: {e}[/red]")
            return False

    def clear_history(self) -> bool:
        """
        Clear all clipboard history.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.history.clear()
            self.save_history()
            return True
        except Exception as e:
            console.print(f"[red]Error clearing history: {e}[/red]")
            return False

    def search_items(
        self, query: str, limit: Optional[int] = None
    ) -> List[ClipboardItem]:
        """
        Search for items containing the query.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching ClipboardItem objects
        """
        if not query.strip():
            return []

        query_lower = query.lower()
        results = []

        for item in self.history:
            if (
                query_lower in item.content.lower()
                or query_lower in item.content_type.lower()
            ):
                results.append(item)

                if limit and len(results) >= limit:
                    break

        return results

    def get_history_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the clipboard history.

        Returns:
            Dictionary containing history statistics
        """
        if not self.history:
            return {
                "total_items": 0,
                "oldest_item": None,
                "newest_item": None,
                "total_content_length": 0,
                "content_types": {},
                "average_content_length": 0,
            }

        content_types = {}
        total_length = 0

        for item in self.history:
            content_types[item.content_type] = (
                content_types.get(item.content_type, 0) + 1
            )
            total_length += item.content_length

        return {
            "total_items": len(self.history),
            "oldest_item": self.history[-1].formatted_timestamp,
            "newest_item": self.history[0].formatted_timestamp,
            "total_content_length": total_length,
            "content_types": content_types,
            "average_content_length": (
                total_length / len(self.history) if self.history else 0
            ),
        }

    def export_history(self, file_path: str, format: str = "json") -> bool:
        """
        Export clipboard history to a file.

        Args:
            file_path: Path to the export file
            format: Export format (json or csv)

        Returns:
            True if successful, False otherwise
        """
        try:
            export_path = Path(file_path)

            if format.lower() == "json":
                data = [item.to_dict() for item in self.history]
                with open(export_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            elif format.lower() == "csv":
                with open(export_path, "w", newline="", encoding="utf-8") as f:
                    if self.history:
                        writer = csv.DictWriter(
                            f, fieldnames=self.history[0].to_dict().keys()
                        )
                        writer.writeheader()
                        for item in self.history:
                            writer.writerow(item.to_dict())
            else:
                console.print(f"[red]Unsupported export format: {format}[/red]")
                return False

            console.print(f"[green]History exported to {export_path}[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Error exporting history: {e}[/red]")
            return False

    def import_history(
        self, file_path: str, format: str = "json", merge: bool = True
    ) -> bool:
        """
        Import clipboard history from a file.

        Args:
            file_path: Path to the import file
            format: Import format (json or csv)
            merge: Whether to merge with existing history

        Returns:
            True if successful, False otherwise
        """
        try:
            import_path = Path(file_path)

            if not import_path.exists():
                console.print(f"[red]Import file not found: {import_path}[/red]")
                return False

            imported_items = []

            if format.lower() == "json":
                with open(import_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item_data in data:
                        imported_items.append(ClipboardItem.from_dict(item_data))

            elif format.lower() == "csv":
                with open(import_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        imported_items.append(ClipboardItem.from_dict(row))
            else:
                console.print(f"[red]Unsupported import format: {format}[/red]")
                return False

            if merge:
                # Merge with existing history, avoiding duplicates
                existing_content = {item.content for item in self.history}
                for item in imported_items:
                    if item.content not in existing_content:
                        self.history.append(item)
                        existing_content.add(item.content)
            else:
                # Replace existing history
                self.history = imported_items

            # Sort by timestamp (newest first) and limit size
            self.history.sort(key=lambda x: x.timestamp, reverse=True)
            if len(self.history) > self.max_history:
                self.history = self.history[: self.max_history]

            self.save_history()
            console.print(f"[green]Imported {len(imported_items)} items[/green]")
            return True

        except Exception as e:
            console.print(f"[red]Error importing history: {e}[/red]")
            return False

    def load_history(self) -> None:
        """Load clipboard history from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = [ClipboardItem.from_dict(item) for item in data]
                    console.print(
                        f"[green]Loaded {len(self.history)} items "
                        f"from history[/green]"
                    )
            else:
                console.print(
                    "[yellow]No existing history found, " "starting fresh[/yellow]"
                )
        except Exception as e:
            console.print(f"[red]Error loading history: {e}[/red]")
            self.history = []

    def save_history(self) -> None:
        """Save clipboard history to storage."""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to file
            data = [item.to_dict() for item in self.history]
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            console.print(f"[red]Error saving history: {e}[/red]")

    def display_history(self, max_preview_length: int = 80) -> None:
        """
        Display the clipboard history in a formatted table.

        Args:
            max_preview_length: Maximum length for content preview
        """
        if not self.history:
            console.print("[yellow]No clipboard history found[/yellow]")
            return

        table = Table(title="📋 Clipper - Your Clipboard History")
        table.add_column("Index", style="cyan", justify="center")
        table.add_column("Timestamp", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Preview", style="white", max_width=max_preview_length)

        for i, item in enumerate(self.history):
            preview = item.content[:max_preview_length]
            if len(item.content) > max_preview_length:
                preview += "..."

            table.add_row(str(i), item.formatted_timestamp, item.content_type, preview)

        console.print(table)

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about the storage system.

        Returns:
            Dictionary containing storage information
        """
        return {
            "storage_path": str(self.storage_path),
            "storage_exists": self.storage_path.exists(),
            "storage_size": (
                self.storage_path.stat().st_size if self.storage_path.exists() else 0
            ),
            "max_history": self.max_history,
            "current_history_size": len(self.history),
            "storage_format": "json",
        }
