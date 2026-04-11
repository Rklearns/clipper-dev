# 🤝 Contributing to clipper-dev

Thank you for your interest in contributing to clipper-dev! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/yourusername/clipper-dev.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes
5. **Test** your changes: `pytest`
6. **Commit** with conventional commits: `git commit -m 'feat: add amazing feature'`
7. **Push** to your branch: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

## 🧪 Development Setup

### Prerequisites

- Python 3.10+
- pip
- git

### Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/clipper-dev.git
cd clipper-dev

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=clipper-dev --cov-report=term-missing

# Run specific test file
pytest tests/test_clipboard.py
```



## 📋 Contribution Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Testing

- Write tests for new functionality
- Maintain test coverage above 90%
- Use descriptive test names
- Test both success and failure cases

### Documentation

- Update docstrings for new functions/classes
- Keep README.md up to date
- Document configuration options
- Provide usage examples

### Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

## 🎯 Areas for Contribution

### High Priority

- 🚀 Performance improvements
- 🐛 Bug fixes
- 📚 Documentation improvements
- 🧪 Test coverage

### Medium Priority

- 🎨 UI/UX enhancements
- 🔧 Additional storage backends
- 📱 Platform-specific optimizations
- 🌍 Internationalization

### Low Priority

- 📊 Analytics and insights
- 🔌 Plugin system
- 📱 Mobile integrations
- 🎭 Additional TUI themes

## 🐛 Reporting Issues

When reporting issues, please include:

- **OS and version**
- **Python version**
- **ClipStack version**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Error messages/logs**

## 💡 Feature Requests

For feature requests:

- Describe the use case
- Explain the benefit
- Suggest implementation approach
- Consider backward compatibility

## 🚀 Pull Request Process

1. **Update** documentation if needed
2. **Add** tests for new functionality
3. **Ensure** all tests pass
4. **Update** CHANGELOG.md
5. **Request** review from maintainers

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/Rklearns/clipper-dev/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Rklearns/clipper-dev/discussions)
- **Email**: your.email@example.com

## 🙏 Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Project documentation

---

**Thank you for contributing to ClipStack! 🚀**
