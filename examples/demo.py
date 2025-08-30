#!/usr/bin/env python3
"""
Demo script for ClipStack.

This script demonstrates the core functionality of ClipStack
and can be used for testing and demonstration purposes.
"""

import time
import sys
from pathlib import Path

# Add the parent directory to the path so we can import clipstack
sys.path.insert(0, str(Path(__file__).parent.parent))

from clipstack.clipboard import ClipboardManager
from clipstack.storage import StorageManager
from clipstack.search import SearchManager
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def demo_clipboard_manager():
    """Demonstrate clipboard manager functionality."""
    console.print(Panel("🔄 Clipboard Manager Demo", style="blue"))
    
    clipboard = ClipboardManager()
    
    # Show status
    status = clipboard.get_status()
    console.print(f"Platform: {status['platform']}")
    console.print(f"Auto Track: {status['auto_track']}")
    
    # Simulate clipboard operations
    console.print("\n📋 Simulating clipboard operations...")
    
    test_contents = [
        "Hello, World!",
        "https://github.com/yourusername/clipstack",
        "def hello_world():\n    print('Hello, World!')",
        "user@example.com",
        "This is a longer text that demonstrates content type detection"
    ]
    
    for i, content in enumerate(test_contents):
        clipboard.set_content(content)
        info = clipboard.get_content_info()
        content_type = clipboard.get_clipboard_type(content)
        
        console.print(f"  {i+1}. {content_type}: {clipboard.format_content_preview(content, 50)}")
        time.sleep(0.5)
    
    return clipboard


def demo_storage_manager():
    """Demonstrate storage manager functionality."""
    console.print(Panel("💾 Storage Manager Demo", style="green"))
    
    # Use temporary storage for demo
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    storage = StorageManager(storage_path=temp_file.name, max_history=10)
    
    # Add some demo items
    demo_items = [
        ("Hello, World!", "text"),
        ("https://github.com/yourusername/clipstack", "url"),
        ("def hello_world():\n    print('Hello, World!')", "code"),
        ("user@example.com", "email"),
        ("This is a longer text that demonstrates content type detection", "long_text")
    ]
    
    for content, content_type in demo_items:
        storage.add_item(content, content_type)
        console.print(f"  ✓ Added {content_type}: {content[:40]}...")
    
    # Show statistics
    stats = storage.get_history_stats()
    console.print(f"\n📊 Statistics:")
    console.print(f"  Total Items: {stats['total_items']}")
    console.print(f"  Content Types: {', '.join(stats['content_types'].keys())}")
    
    # Display history
    console.print(f"\n📋 History:")
    storage.display_history(max_preview_length=60)
    
    # Clean up
    import os
    os.unlink(temp_file.name)
    
    return storage


def demo_search_manager():
    """Demonstrate search manager functionality."""
    console.print(Panel("🔍 Search Manager Demo", style="yellow"))
    
    # Create some demo items
    from clipstack.storage import ClipboardItem
    
    demo_items = [
        ClipboardItem("python function example", 1234567890.0, "code", 25, 1, 3),
        ClipboardItem("javascript code sample", 1234567891.0, "code", 24, 1, 3),
        ClipboardItem("https://python.org", 1234567892.0, "url", 20, 1, 1),
        ClipboardItem("user@example.com", 1234567893.0, "email", 16, 1, 1),
        ClipboardItem("random text content", 1234567894.0, "text", 20, 1, 3)
    ]
    
    search_mgr = SearchManager()
    
    # Fuzzy search
    console.print("🔍 Fuzzy Search Results:")
    results = search_mgr.fuzzy_search(demo_items, "python", limit=3)
    for item, score in results:
        console.print(f"  {score:.1f}%: {item.content}")
    
    # Content type search
    console.print("\n📝 Content Type Search (code):")
    code_results = search_mgr.content_type_search(demo_items, "code")
    for item in code_results:
        console.print(f"  {item.content}")
    
    # Advanced search
    console.print("\n⚡ Advanced Search:")
    advanced_results = search_mgr.advanced_search(
        demo_items, 
        "python", 
        search_type="fuzzy",
        content_type="code"
    )
    for item in advanced_results:
        console.print(f"  {item.content}")


def demo_cli_commands():
    """Demonstrate CLI command functionality."""
    console.print(Panel("🖥️ CLI Commands Demo", style="magenta"))
    
    console.print("Available commands:")
    console.print("  clipstack add          - Add current clipboard content")
    console.print("  clipstack list         - Show clipboard history")
    console.print("  clipstack search       - Search history")
    console.print("  clipstack peek         - Show latest item")
    console.print("  clipstack pop          - Restore last item")
    console.print("  clipstack restore <n>  - Restore item by index")
    console.print("  clipstack clear        - Clear history")
    console.print("  clipstack export       - Export to file")
    console.print("  clipstack import       - Import from file")
    console.print("  clipstack stats        - Show statistics")
    console.print("  clipstack info         - System information")
    console.print("  clipstack tui          - Interactive interface")
    console.print("  clipstack monitor      - Real-time monitoring")
    
    console.print("\nTry running: clipstack --help")


def main():
    """Run the complete demo."""
    console.print(Panel.fit(
        "🚀 ClipStack Demo",
        style="bold blue",
        subtitle="A powerful clipboard manager for developers"
    ))
    
    try:
        # Run demos
        demo_clipboard_manager()
        console.print()
        
        demo_storage_manager()
        console.print()
        
        demo_search_manager()
        console.print()
        
        demo_cli_commands()
        
        console.print(Panel(
            "✨ Demo completed successfully!",
            style="bold green"
        ))
        
        console.print("\nTo get started with ClipStack:")
        console.print("1. Install: pip install -e .")
        console.print("2. Try: clipstack --help")
        console.print("3. Add content: clipstack add")
        console.print("4. View history: clipstack list")
        console.print("5. Search: clipstack search 'python'")
        
    except Exception as e:
        console.print(f"[red]Demo failed: {e}[/red]")
        console.print("Make sure ClipStack is properly installed and configured.")


if __name__ == "__main__":
    main()
