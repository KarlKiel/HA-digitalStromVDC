# Contributing to digitalSTROM VDC Integration

Thank you for your interest in contributing to the digitalSTROM VDC Integration for Home Assistant! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11 or newer
- Home Assistant Core development environment
- Git
- Basic knowledge of Home Assistant integration development

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/KarlKiel/HA-digitalStromVDC.git
   cd HA-digitalStromVDC
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_dev.txt
   ```

4. **Install development tools**
   ```bash
   pip install black pylint mypy pre-commit
   pre-commit install
   ```

5. **Set up Home Assistant development instance**
   ```bash
   # Install Home Assistant Core
   pip install homeassistant
   
   # Create config directory
   mkdir -p config/custom_components
   
   # Symlink integration for testing
   ln -s $(pwd)/custom_components/digitalstrom_vdc config/custom_components/
   ```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_config_flow.py

# Run with coverage
pytest tests/ --cov=custom_components.digitalstrom_vdc --cov-report=html
```

### Code Quality

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Pylint**: Code linting
- **MyPy**: Type checking
- **Pre-commit**: Git hooks for automated checks

Run checks manually:
```bash
# Format code
black custom_components/digitalstrom_vdc

# Lint code
pylint custom_components/digitalstrom_vdc

# Type check
mypy custom_components/digitalstrom_vdc
```

## Development Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for all functions
- Maximum line length: 88 characters (Black default)
- Use descriptive variable and function names
- Add docstrings to all classes and functions

### Example:
```python
"""Module description."""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class MyClass:
    """Class description."""

    def __init__(self, param: str) -> None:
        """Initialize MyClass.
        
        Args:
            param: Description of parameter
        """
        self._param = param

    async def my_method(self, value: int) -> dict[str, Any]:
        """Method description.
        
        Args:
            value: Description of value
            
        Returns:
            Dictionary with results
        """
        return {"result": value}
```

### Commit Messages

Follow conventional commit format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

**Example:**
```
feat(device): add support for RGB lights

Implement RGB color control for light platform
using DSChannelType color channels.

Closes #42
```

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`

### Pull Request Process

1. **Create a branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test your changes**
   ```bash
   pytest tests/
   black custom_components/digitalstrom_vdc
   pylint custom_components/digitalstrom_vdc
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push to GitHub**
   ```bash
   git push origin feature/my-new-feature
   ```

6. **Create Pull Request**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in PR template
   - Submit for review

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts

## Testing Guidelines

### Unit Tests

Write unit tests for all new functionality:

```python
"""Tests for my_module."""
import pytest
from custom_components.digitalstrom_vdc.my_module import MyClass


async def test_my_function():
    """Test my_function."""
    obj = MyClass("test")
    result = await obj.my_method(42)
    assert result == {"result": 42}
```

### Integration Tests

For integration testing with Home Assistant:

```python
"""Integration tests."""
from homeassistant.setup import async_setup_component


async def test_integration_setup(hass):
    """Test integration setup."""
    assert await async_setup_component(
        hass,
        "digitalstrom_vdc",
        {}
    )
```

### Test Coverage

- Aim for 80%+ code coverage
- All new features must have tests
- All bug fixes should include regression tests

## Documentation

### Code Documentation

- All modules should have module docstrings
- All classes should have class docstrings
- All public methods should have docstrings
- Use Google style docstrings

### User Documentation

Update relevant documentation when adding features:

- `README.md`: Overview and quick start
- `docs/INSTALLATION.md`: Installation instructions
- `docs/TROUBLESHOOTING.md`: Common issues
- Template documentation for new templates

## Release Process

Maintainers follow this process for releases:

1. Update version in `manifest.json`
2. Update `CHANGELOG.md`
3. Create Git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions creates release automatically
6. Update HACS default repository (if applicable)

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- Additional platform implementations (climate, cover improvements)
- Enhanced entity binding system
- Template system improvements
- Comprehensive testing

### Medium Priority
- Additional device templates
- Performance optimizations
- UI/UX improvements
- Documentation improvements

### Low Priority
- Example configurations
- Translations
- Integration with other systems

## Getting Help

- **Questions**: Open a [discussion](https://github.com/KarlKiel/HA-digitalStromVDC/discussions)
- **Bugs**: Open an [issue](https://github.com/KarlKiel/HA-digitalStromVDC/issues)
- **Feature Requests**: Open an issue with `enhancement` label

## Code of Conduct

Be respectful and inclusive. We follow the [Home Assistant Code of Conduct](https://www.home-assistant.io/code_of_conduct/).

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.

---

Thank you for contributing to the digitalSTROM VDC Integration! 🎉
