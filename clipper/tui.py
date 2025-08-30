"""
Terminal User Interface (TUI) for ClipStack.

This module provides an interactive terminal interface using Textual
for browsing and managing clipboard history.
"""

from typing import Optional, List
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Static, Button, Input, 
    DataTable, Label, TabbedContent, TabPane
)
from textual.widgets.data_table import RowKey
from textual.reactive import reactive
from rich.text import Text
from rich.console import Console

from .storage import StorageManager, ClipboardItem
from .search import SearchManager
from .clipboard import ClipboardManager

console = Console()


class ClipStackTUI(App):
    """
    Terminal User Interface for ClipStack.
    
    Provides an interactive interface for browsing clipboard history,
    searching, and managing clipboard items.
    """
    
    CSS = """
    DataTable {
        height: 1fr;
    }
    
    .search-container {
        height: auto;
        margin: 1;
    }
    
    .status-bar {
        height: auto;
        margin: 1;
        padding: 1;
        background: $accent;
        color: $text;
    }
    
    .content-preview {
        height: 1fr;
        margin: 1;
        padding: 1;
        border: solid $accent;
    }
    
    TabPane {
        padding: 1;
    }
    """
    
    def __init__(self):
        """Initialize the TUI application."""
        super().__init__()
        self.storage = StorageManager()
        self.search_manager = SearchManager()
        self.clipboard_manager = ClipboardManager()
        self.current_selection: Optional[ClipboardItem] = None
    
    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)
        
        with TabbedContent():
            with TabPane("📋 History", id="history"):
                yield Container(
                    Label("Search:", classes="search-container"),
                    Input(placeholder="Type to search...", id="search-input"),
                    DataTable(id="history-table"),
                    classes="search-container"
                )
            
            with TabPane("🔍 Search", id="search"):
                yield Container(
                    Label("Advanced Search:", classes="search-container"),
                    Input(placeholder="Search query...", id="advanced-search-input"),
                    DataTable(id="search-results-table"),
                    classes="search-container"
                )
            
            with TabPane("📊 Stats", id="stats"):
                yield Container(
                    Label("Clipboard Statistics", classes="status-bar"),
                    Static("", id="stats-content"),
                    classes="content-preview"
                )
            
            with TabPane("⚙️ Settings", id="settings"):
                yield Container(
                    Label("Settings", classes="status-bar"),
                    Static("", id="settings-content"),
                    classes="content-preview"
                )
        
        with Container(classes="status-bar"):
            yield Label("Ready", id="status-label")
            yield Button("Refresh", id="refresh-btn")
            yield Button("Clear History", id="clear-btn")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle application mount."""
        self.title = "ClipStack - Clipboard Manager"
        self.sub_title = "Interactive Terminal Interface"
        
        # Setup history table
        history_table = self.query_one("#history-table", DataTable)
        history_table.add_columns("Index", "Timestamp", "Type", "Preview")
        
        # Setup search results table
        search_table = self.query_one("#search-results-table", DataTable)
        search_table.add_columns("Index", "Score", "Timestamp", "Type", "Preview")
        
        # Load initial data
        self.refresh_history()
        self.update_stats()
        self.update_settings()
        
        # Focus on search input
        search_input = self.query_one("#search-input", Input)
        search_input.focus()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for search."""
        if event.input.id == "search-input":
            self.perform_search(event.value)
        elif event.input.id == "advanced-search-input":
            self.perform_advanced_search(event.value)
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle table row selection."""
        table = event.data_table
        row_key = event.row_key
        
        if table.id == "history-table":
            self.select_history_item(row_key)
        elif table.id == "search-results-table":
            self.select_search_item(row_key)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "refresh-btn":
            self.refresh_history()
        elif event.button.id == "clear-btn":
            self.clear_history()
    
    def perform_search(self, query: str) -> None:
        """Perform search on clipboard history."""
        if not query.strip():
            self.refresh_history()
            return
        
        # Perform fuzzy search
        search_results = self.search_manager.fuzzy_search(
            self.storage.history, query, limit=50
        )
        
        # Update history table with search results
        history_table = self.query_one("#history-table", DataTable)
        history_table.clear()
        
        for i, (item, score) in enumerate(search_results):
            preview = item.content[:60] + "..." if len(item.content) > 60 else item.content
            history_table.add_row(
                str(i),
                item.formatted_timestamp,
                item.content_type,
                preview,
                key=f"search_{i}"
            )
        
        # Update status
        status_label = self.query_one("#status-label", Label)
        status_label.update(f"Found {len(search_results)} results for '{query}'")
    
    def perform_advanced_search(self, query: str) -> None:
        """Perform advanced search with multiple options."""
        if not query.strip():
            return
        
        # For now, just do fuzzy search
        # In a full implementation, you'd parse the query for advanced options
        search_results = self.search_manager.fuzzy_search(
            self.storage.history, query, limit=50
        )
        
        # Update search results table
        search_table = self.query_one("#search-results-table", DataTable)
        search_table.clear()
        
        for i, (item, score) in enumerate(search_results):
            preview = item.content[:60] + "..." if len(item.content) > 60 else item.content
            search_table.add_row(
                str(i),
                f"{score:.1f}%",
                item.formatted_timestamp,
                item.content_type,
                preview,
                key=f"advanced_{i}"
            )
    
    def select_history_item(self, row_key: RowKey) -> None:
        """Handle selection of a history item."""
        try:
            index = int(str(row_key).split('_')[1])
            if 0 <= index < len(self.storage.history):
                item = self.storage.history[index]
                self.current_selection = item
                
                # Copy to clipboard
                if self.clipboard_manager.set_content(item.content):
                    status_label = self.query_one("#status-label", Label)
                    status_label.update(f"Copied item {index} to clipboard")
                else:
                    status_label = self.query_one("#status-label", Label)
                    status_label.update(f"Failed to copy item {index}")
        except (ValueError, IndexError):
            pass
    
    def select_search_item(self, row_key: RowKey) -> None:
        """Handle selection of a search result item."""
        try:
            index = int(str(row_key).split('_')[1])
            # Find the actual item in history
            # This is a simplified version - in practice you'd maintain a mapping
            pass
        except (ValueError, IndexError):
            pass
    
    def refresh_history(self) -> None:
        """Refresh the history display."""
        history_table = self.query_one("#history-table", DataTable)
        history_table.clear()
        
        for i, item in enumerate(self.storage.history):
            preview = item.content[:60] + "..." if len(item.content) > 60 else item.content
            history_table.add_row(
                str(i),
                item.formatted_timestamp,
                item.content_type,
                preview,
                key=f"history_{i}"
            )
        
        # Update status
        status_label = self.query_one("#status-label", Label)
        status_label.update(f"Loaded {len(self.storage.history)} items")
    
    def clear_history(self) -> None:
        """Clear the clipboard history."""
        if self.storage.clear_history():
            self.refresh_history()
            status_label = self.query_one("#status-label", Label)
            status_label.update("History cleared")
        else:
            status_label = self.query_one("#status-label", Label)
            status_label.update("Failed to clear history")
    
    def update_stats(self) -> None:
        """Update the statistics display."""
        stats = self.storage.get_history_stats()
        stats_content = self.query_one("#stats-content", Static)
        
        stats_text = f"""
        📊 Clipboard Statistics
        
        Total Items: {stats['total_items']}
        Oldest Item: {stats['oldest_item'] or 'N/A'}
        Newest Item: {stats['newest_item'] or 'N/A'}
        Total Content Length: {stats['total_content_length']:,} characters
        Average Content Length: {stats['average_content_length']:.1f} characters
        
        Content Types:
        """
        
        for content_type, count in stats['content_types'].items():
            stats_text += f"  {content_type}: {count}\n"
        
        stats_content.update(stats_text)
    
    def update_settings(self) -> None:
        """Update the settings display."""
        storage_info = self.storage.get_storage_info()
        clipboard_status = self.clipboard_manager.get_status()
        
        settings_content = self.query_one("#settings-content", Static)
        
        settings_text = f"""
        ⚙️ Application Settings
        
        Storage:
          Path: {storage_info['storage_path']}
          Format: {storage_info['storage_format']}
          Max History: {storage_info['max_history']}
          Current Size: {storage_info['current_history_size']}
        
        Clipboard:
          Platform: {clipboard_status['platform']}
          Auto Track: {clipboard_status['auto_track']}
          Track Interval: {clipboard_status['track_interval']}s
          Monitoring: {clipboard_status['monitoring']}
        """
        
        settings_content.update(settings_text)
    
    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "ctrl+r":
            self.refresh_history()
        elif event.key == "ctrl+q":
            self.exit()
        elif event.key == "ctrl+s":
            # Focus search
            search_input = self.query_one("#search-input", Input)
            search_input.focus()
    
    def on_exit(self) -> None:
        """Handle application exit."""
        # Stop clipboard monitoring if active
        if self.clipboard_manager.is_monitoring():
            self.clipboard_manager.stop_monitoring()


def run_tui() -> None:
    """Run the TUI application."""
    try:
        app = ClipStackTUI()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]TUI interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error running TUI: {e}[/red]")


if __name__ == "__main__":
    run_tui()
