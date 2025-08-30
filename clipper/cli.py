"""
Command Line Interface for Clipper.

This module provides the main CLI interface using Typer, with all
the commands and options for managing clipboard history.
"""

import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .clipboard import ClipboardManager
from .storage import StorageManager
from .search import SearchManager
from .tui import run_tui

# Initialize Typer app
app = typer.Typer(
    name="clipper",
    help="A powerful, cross-platform clipboard manager for developers",
    add_completion=False,
    rich_markup_mode="rich"
)

# Initialize console
console = Console()

# Global managers
clipboard_manager: Optional[ClipboardManager] = None
storage_manager: Optional[StorageManager] = None
search_manager: Optional[SearchManager] = None


def get_managers():
    """Get or initialize the global managers."""
    global clipboard_manager, storage_manager, search_manager
    
    if clipboard_manager is None:
        clipboard_manager = ClipboardManager()
    if storage_manager is None:
        storage_manager = StorageManager()
    if search_manager is None:
        search_manager = SearchManager()
    
    return clipboard_manager, storage_manager, search_manager


@app.command()
def add(
    content: Optional[str] = typer.Argument(None, help="Content to add (if not provided, uses current clipboard)"),
    content_type: str = typer.Option("text", "--type", "-t", help="Type of content being added")
) -> None:
    """Add content to clipboard history."""
    clipboard, storage, _ = get_managers()
    
    if content is None:
        # Get content from current clipboard
        content = clipboard.get_content()
        if not content.strip():
            console.print("[red]No content in clipboard to add[/red]")
            raise typer.Exit(1)
    
    # Determine content type if not specified
    if content_type == "text":
        content_type = clipboard.get_clipboard_type(content)
    
    # Add to history
    if storage.add_item(content, content_type):
        console.print(f"[green]✓ Added {content_type} to clipboard history[/green]")
        console.print(f"[dim]Content: {clipboard.format_content_preview(content)}[/dim]")
    else:
        console.print("[red]Failed to add item to history[/red]")
        raise typer.Exit(1)


@app.command()
def list(
    max_preview: int = typer.Option(80, "--preview", "-p", help="Maximum preview length"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of items to show")
) -> None:
    """List clipboard history."""
    _, storage, _ = get_managers()
    
    if not storage.history:
        console.print("[yellow]No clipboard history found[/yellow]")
        return
    
    # Apply limit if specified
    items_to_show = storage.history[:limit] if limit else storage.history
    
    # Create table
    table = Table(title="📋 Clipper - Your Clipboard History")
    table.add_column("Index", style="cyan", justify="center")
    table.add_column("Timestamp", style="green")
    table.add_column("Type", style="blue")
    table.add_column("Preview", style="white", max_width=max_preview)
    
    for i, item in enumerate(items_to_show):
        preview = clipboard_manager.format_content_preview(item.content, max_preview)
        table.add_row(
            str(i),
            item.formatted_timestamp,
            item.content_type,
            preview
        )
    
    console.print(table)
    console.print(f"[dim]Showing {len(items_to_show)} of {len(storage.history)} items[/dim]")


@app.command()
def peek() -> None:
    """Show the most recent clipboard item."""
    _, storage, _ = get_managers()
    
    latest = storage.get_latest()
    if not latest:
        console.print("[yellow]No clipboard history found[/yellow]")
        return
    
    console.print(Panel(
        Text(latest.content, style="white"),
        title=f"📋 Latest Clipboard Item ({latest.content_type})",
        subtitle=f"Copied at {latest.formatted_timestamp}",
        border_style="green"
    ))


@app.command()
def pop() -> None:
    """Restore the last copied item to clipboard."""
    clipboard, storage, _ = get_managers()
    
    latest = storage.get_latest()
    if not latest:
        console.print("[red]No clipboard history found[/red]")
        raise typer.Exit(1)
    
    if clipboard.set_content(latest.content):
        console.print(f"[green]✓ Restored item to clipboard[/green]")
        console.print(f"[dim]Content: {clipboard.format_content_preview(latest.content)}[/dim]")
    else:
        console.print("[red]Failed to restore item to clipboard[/red]")
        raise typer.Exit(1)


@app.command()
def restore(
    index: int = typer.Argument(..., help="Index of the item to restore")
) -> None:
    """Restore a specific item by index."""
    clipboard, storage, _ = get_managers()
    
    item = storage.get_item(index)
    if not item:
        console.print(f"[red]No item found at index {index}[/red]")
        raise typer.Exit(1)
    
    if clipboard.set_content(item.content):
        console.print(f"[green]✓ Restored item {index} to clipboard[/green]")
        console.print(f"[dim]Content: {clipboard.format_content_preview(item.content)}[/dim]")
    else:
        console.print("[red]Failed to restore item to clipboard[/red]")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    search_type: str = typer.Option("fuzzy", "--type", "-t", help="Search type (fuzzy, exact, regex)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of results")
) -> None:
    """Search clipboard history."""
    _, storage, search_mgr = get_managers()
    
    if not storage.history:
        console.print("[yellow]No clipboard history to search[/yellow]")
        return
    
    # Perform search
    search_mgr.search_and_display(
        storage.history, 
        query, 
        search_type, 
        max_preview_length=80
    )


@app.command()
def clear() -> None:
    """Clear entire clipboard history."""
    _, storage, _ = get_managers()
    
    if not storage.history:
        console.print("[yellow]No clipboard history to clear[/yellow]")
        return
    
    # Confirm action
    if not typer.confirm("Are you sure you want to clear all clipboard history?"):
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    
    if storage.clear_history():
        console.print("[green]✓ Clipboard history cleared[/green]")
    else:
        console.print("[red]Failed to clear clipboard history[/red]")
        raise typer.Exit(1)


@app.command()
def export(
    file_path: str = typer.Argument(..., help="Path to export file"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, csv)")
) -> None:
    """Export clipboard history to a file."""
    _, storage, _ = get_managers()
    
    if not storage.history:
        console.print("[yellow]No clipboard history to export[/yellow]")
        return
    
    # Determine format from file extension if not specified
    if format == "json" and not file_path.endswith(('.json', '.csv')):
        if file_path.endswith('.csv'):
            format = "csv"
        elif not file_path.endswith('.json'):
            file_path += '.json'
    
    if storage.export_history(file_path, format):
        console.print(f"[green]✓ History exported to {file_path}[/green]")
    else:
        console.print("[red]Failed to export history[/red]")
        raise typer.Exit(1)


@app.command()
def import_history(
    file_path: str = typer.Argument(..., help="Path to import file"),
    format: str = typer.Option("auto", "--format", "-f", help="Import format (json, csv, auto)"),
    merge: bool = typer.Option(True, "--merge/--replace", help="Merge with existing history or replace")
) -> None:
    """Import clipboard history from a file."""
    _, storage, _ = get_managers()
    
    # Auto-detect format if not specified
    if format == "auto":
        if file_path.endswith('.csv'):
            format = "csv"
        elif file_path.endswith('.json'):
            format = "json"
        else:
            console.print("[red]Could not determine file format. Please specify with --format[/red]")
            raise typer.Exit(1)
    
    if storage.import_history(file_path, format, merge):
        console.print(f"[green]✓ History imported from {file_path}[/green]")
    else:
        console.print("[red]Failed to import history[/red]")
        raise typer.Exit(1)


@app.command()
def stats() -> None:
    """Show clipboard history statistics."""
    _, storage, _ = get_managers()
    
    stats_data = storage.get_history_stats()
    
    if not stats_data['total_items']:
        console.print("[yellow]No clipboard history found[/yellow]")
        return
    
    # Create stats table
    table = Table(title="📊 Clipboard Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Total Items", str(stats_data['total_items']))
    table.add_row("Oldest Item", stats_data['oldest_item'] or 'N/A')
    table.add_row("Newest Item", stats_data['newest_item'] or 'N/A')
    table.add_row("Total Content Length", f"{stats_data['total_content_length']:,} characters")
    table.add_row("Average Content Length", f"{stats_data['average_content_length']:.1f} characters")
    
    console.print(table)
    
    # Content type breakdown
    if stats_data['content_types']:
        type_table = Table(title="Content Type Breakdown")
        type_table.add_column("Type", style="blue")
        type_table.add_column("Count", style="cyan", justify="center")
        
        for content_type, count in stats_data['content_types'].items():
            type_table.add_row(content_type, str(count))
        
        console.print(type_table)


@app.command()
def info() -> None:
    """Show system information and status."""
    clipboard, storage, _ = get_managers()
    
    # Clipboard status
    clipboard_status = clipboard.get_status()
    storage_info = storage.get_storage_info()
    
    # Create info table
    table = Table(title="ℹ️ Clipper System Information")
    table.add_column("Category", style="cyan")
    table.add_column("Details", style="white")
    
    table.add_row("Clipboard Platform", clipboard_status['platform'])
    table.add_row("Auto Track", str(clipboard_status['auto_track']))
    table.add_row("Track Interval", f"{clipboard_status['track_interval']}s")
    table.add_row("Monitoring", str(clipboard_status['monitoring']))
    table.add_row("Storage Path", storage_info['storage_path'])
    table.add_row("Storage Format", storage_info['storage_format'])
    table.add_row("Max History", str(storage_info['max_history']))
    table.add_row("Current History Size", str(storage_info['current_history_size']))
    
    console.print(table)


@app.command()
def tui() -> None:
    """Launch the interactive terminal user interface."""
    console.print("[green]Launching Clipper TUI...[/green]")
    run_tui()


@app.command()
def monitor(
    interval: float = typer.Option(1.0, "--interval", "-i", help="Check interval in seconds")
) -> None:
    """Start monitoring clipboard changes."""
    clipboard, storage, _ = get_managers()
    
    def on_clipboard_change(content: str):
        """Callback for clipboard changes."""
        content_type = clipboard.get_clipboard_type(content)
        if storage.add_item(content, content_type):
            console.print(f"[green]✓ Auto-added {content_type} to history[/green]")
    
    console.print(f"[green]Starting clipboard monitoring (interval: {interval}s)[/green]")
    console.print("[yellow]Press Ctrl+C to stop monitoring[/yellow]")
    
    try:
        clipboard.track_interval = interval
        clipboard.start_monitoring(on_clipboard_change)
    except KeyboardInterrupt:
        clipboard.stop_monitoring()
        console.print("\n[yellow]Monitoring stopped[/yellow]")


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Configuration file path")
) -> None:
    """
    Clipper - A powerful, cross-platform clipboard manager for developers.
    
    Manage your clipboard history with ease. Copy, search, and restore
    your copied content with lightning-fast search and beautiful output.
    """
    if version:
        from . import __version__
        console.print(f"Clipper version {__version__}")
        raise typer.Exit()
    
    # Load configuration if specified
    if config_file:
        # TODO: Implement configuration loading
        pass


if __name__ == "__main__":
    app()
