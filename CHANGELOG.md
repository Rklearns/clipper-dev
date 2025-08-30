# 📋 Changelog

All notable changes to ClipStack will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- SQLite storage backend
- Plugin system
- Additional search algorithms
- Performance optimizations

## [0.1.0] - 2024-08-30

### 🎉 Initial Release

**ClipStack** is now available on PyPI! This is the first public release with all core functionality.

### ✨ Added

- **Core Clipboard Management**
  - Add clipboard content to history
  - List clipboard history with timestamps
  - Peek at most recent clipboard item
  - Pop last copied item to clipboard
  - Restore specific items by index

- **Advanced Search**
  - Fuzzy search with rapidfuzz
  - Configurable search algorithms
  - Search result highlighting
  - Search history and statistics

- **Storage & Persistence**
  - JSON-based storage system
  - Automatic duplicate detection
  - Configurable history limits
  - Import/export functionality

- **User Interface**
  - Rich terminal output with colors
  - Interactive TUI mode
  - Beautiful tables and formatting
  - Cross-platform compatibility

- **Developer Features**
  - Comprehensive test coverage
  - Type hints throughout
  - Extensive documentation
  - Modern Python packaging

### 🔧 Technical Features

- **Cross-Platform Support**
  - macOS (pbcopy/pbpaste)
  - Linux (xclip/xsel)
  - Windows (pywin32)

- **Performance Optimizations**
  - Efficient search algorithms
  - Memory-conscious storage
  - Fast startup times
  - Responsive TUI

- **Quality Assurance**
  - 54 passing tests
  - Code formatting with Black
  - Linting with flake8
  - Type checking with mypy

### 📦 Distribution

- **PyPI Package**: `pip install clipstack`
- **Source Distribution**: Available on GitHub
- **Documentation**: Comprehensive README and guides
- **License**: MIT License

---

## 📝 Version History

- **0.1.0**: Initial public release with full functionality
- **Future**: Planned features and improvements

---

For more information about changes, see our [GitHub repository](https://github.com/yourusername/clipstack).
