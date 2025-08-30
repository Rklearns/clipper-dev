"""
Clipboard management functionality for ClipStack.

This module handles all clipboard operations including reading, writing,
and monitoring clipboard changes across different platforms.
"""

import time
from typing import Optional, Callable
from pathlib import Path
import pyperclip
from rich.console import Console
from rich.text import Text

console = Console()


class ClipboardManager:
    """
    Manages clipboard operations and monitoring.
    
    This class provides a unified interface for clipboard operations
    across different platforms, with support for monitoring clipboard
    changes and handling clipboard content.
    """
    
    def __init__(self, auto_track: bool = True, track_interval: float = 1.0):
        """
        Initialize the clipboard manager.
        
        Args:
            auto_track: Whether to automatically track clipboard changes
            track_interval: Interval in seconds between clipboard checks
        """
        self.auto_track = auto_track
        self.track_interval = track_interval
        self.last_content: Optional[str] = None
        self.monitoring = False
        self._monitor_callback: Optional[Callable[[str], None]] = None
        
    def get_content(self) -> str:
        """
        Get the current clipboard content.
        
        Returns:
            The current clipboard content as a string.
            
        Raises:
            pyperclip.PyperclipException: If clipboard access fails
        """
        try:
            content = pyperclip.paste()
            return content if content else ""
        except pyperclip.PyperclipException as e:
            console.print(f"[red]Error accessing clipboard: {e}[/red]")
            return ""
    
    def set_content(self, content: str) -> bool:
        """
        Set the clipboard content.
        
        Args:
            content: The content to set in the clipboard
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyperclip.copy(content)
            self.last_content = content
            return True
        except pyperclip.PyperclipException as e:
            console.print(f"[red]Error setting clipboard: {e}[/red]")
            return False
    
    def has_changed(self) -> bool:
        """
        Check if clipboard content has changed since last check.
        
        Returns:
            True if content has changed, False otherwise
        """
        current_content = self.get_content()
        if current_content != self.last_content:
            self.last_content = current_content
            return True
        return False
    
    def get_content_info(self) -> dict:
        """
        Get detailed information about the current clipboard content.
        
        Returns:
            Dictionary containing content information
        """
        content = self.get_content()
        return {
            "content": content,
            "length": len(content),
            "lines": len(content.splitlines()),
            "words": len(content.split()),
            "is_empty": not content.strip(),
            "timestamp": time.time()
        }
    
    def start_monitoring(self, callback: Callable[[str], None]) -> None:
        """
        Start monitoring clipboard changes.
        
        Args:
            callback: Function to call when clipboard content changes
        """
        if self.monitoring:
            console.print("[yellow]Clipboard monitoring is already active[/yellow]")
            return
            
        self._monitor_callback = callback
        self.monitoring = True
        self.last_content = self.get_content()
        
        console.print("[green]Started clipboard monitoring[/green]")
        
        try:
            while self.monitoring:
                if self.has_changed() and self._monitor_callback:
                    self._monitor_callback(self.last_content)
                time.sleep(self.track_interval)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self) -> None:
        """Stop monitoring clipboard changes."""
        self.monitoring = False
        console.print("[yellow]Stopped clipboard monitoring[/yellow]")
    
    def is_monitoring(self) -> bool:
        """
        Check if clipboard monitoring is active.
        
        Returns:
            True if monitoring is active, False otherwise
        """
        return self.monitoring
    
    def get_status(self) -> dict:
        """
        Get the current status of the clipboard manager.
        
        Returns:
            Dictionary containing status information
        """
        platform_info = pyperclip.determine_clipboard()
        # Convert platform info to string if it's a tuple
        if isinstance(platform_info, tuple):
            platform_str = "macOS (pbcopy/pbpaste)"
        else:
            platform_str = str(platform_info)
            
        return {
            "auto_track": self.auto_track,
            "track_interval": self.track_interval,
            "monitoring": self.monitoring,
            "last_content_length": len(self.last_content) if self.last_content else 0,
            "platform": platform_str
        }
    
    def validate_content(self, content: str) -> bool:
        """
        Validate clipboard content.
        
        Args:
            content: Content to validate
            
        Returns:
            True if content is valid, False otherwise
        """
        if not isinstance(content, str):
            return False
        
        # Check for reasonable size limits (10MB)
        if len(content.encode('utf-8')) > 10 * 1024 * 1024:
            return False
            
        return True
    
    def format_content_preview(self, content: str, max_length: int = 80) -> str:
        """
        Format content for preview display.
        
        Args:
            content: Content to format
            max_length: Maximum length for preview
            
        Returns:
            Formatted preview string
        """
        if not content:
            return "[empty]"
        
        # Remove extra whitespace and newlines
        cleaned = " ".join(content.split())
        
        if len(cleaned) <= max_length:
            return cleaned
        
        return cleaned[:max_length-3] + "..."
    
    def get_clipboard_type(self, content: str) -> str:
        """
        Determine the type of clipboard content.
        
        Args:
            content: Content to analyze
            
        Returns:
            String describing the content type
        """
        if not content:
            return "empty"
        
        lines = content.splitlines()
        
        if len(lines) == 1:
            if content.startswith(('http://', 'https://')):
                return "url"
            elif content.count('@') == 1 and '.' in content:
                return "email"
            elif len(content) <= 50:
                return "short_text"
            else:
                return "long_text"
        else:
            if any(line.strip().startswith(('#', '//', '/*', '*')) for line in lines):
                return "code"
            elif len(lines) > 10:
                return "long_text"
            else:
                return "multi_line_text"
