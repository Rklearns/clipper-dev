"""
ClipStack - A powerful, cross-platform clipboard manager for developers.

A terminal-first clipboard manager that helps developers never lose their copied content.
Built with Python and designed for productivity, it provides instant access to your
clipboard history with lightning-fast search and seamless cross-platform support.
"""

__version__ = "0.1.0"
__author__ = "ClipStack Contributors"
__email__ = "your.email@example.com"
__license__ = "MIT"
__url__ = "https://github.com/yourusername/clipstack"

from .clipboard import ClipboardManager
from .storage import StorageManager
from .search import SearchManager

__all__ = [
    "ClipboardManager",
    "StorageManager", 
    "SearchManager",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
]
