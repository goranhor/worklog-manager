# Contributing to Worklog Manager

Thank you for your interest in contributing to Worklog Manager! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

### Our Standards

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the project
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/worklog-manager.git
   cd worklog-manager
   ```
3. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites
- Python 3.7 or higher
- Git for version control
- A code editor (VS Code recommended)

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/worklog-manager.git
cd worklog-manager

# Run the application
python main.py
```

### Project Structure
```
worklog-manager/
├── main.py              # Application entry point
├── gui/                 # User interface components
├── core/                # Business logic
├── data/                # Database and models
├── exporters/           # Export functionality
├── tests/               # Test suite
└── docs/                # Documentation
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When reporting bugs, include:**
- Clear descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version)
- Relevant log files from `logs/` directory

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**When suggesting enhancements, include:**
- Clear use case and benefits
- Detailed description of proposed functionality
- Mockups or examples (if applicable)
- Potential implementation approach

### Contributing Code

1. **Choose an issue** to work on or create one
2. **Comment** on the issue to let others know you're working on it
3. **Fork and branch** from `main`
4. **Implement** your changes
5. **Test** thoroughly
6. **Submit** a pull request

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines:

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings to all functions, classes, and modules
- Use type hints where appropriate

**Example:**
```python
def calculate_productive_time(start_time: datetime, end_time: datetime) -> int:
    """
    Calculate productive work time in minutes.
    
    Args:
        start_time: Start of work session
        end_time: End of work session
        
    Returns:
        Productive time in minutes
    """
    delta = end_time - start_time
    return int(delta.total_seconds() / 60)
```

### Code Organization

- Keep functions focused and single-purpose
- Limit function complexity (max 15-20 lines recommended)
- Use meaningful comments for complex logic
- Organize imports: standard library, third-party, local
- Avoid circular dependencies

### GUI Guidelines

- Follow existing UI patterns and conventions
- Maintain consistent spacing and alignment
- Provide user feedback for all actions
- Handle errors gracefully with user-friendly messages
- Support keyboard shortcuts where applicable

## Testing Guidelines

### Writing Tests

- Write tests for new features and bug fixes
- Aim for high test coverage (minimum 70%)
- Test edge cases and error conditions
- Use descriptive test names

**Example:**
```python
def test_calculate_overtime_positive():
    """Test overtime calculation when work exceeds norm."""
    work_minutes = 480  # 8 hours
    result = calculate_overtime(work_minutes, work_norm=450)
    assert result == 30
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_time_calculator.py

# Run with coverage
python -m pytest --cov=. tests/
```

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(export): add PDF export functionality

Implement PDF export using ReportLab library.
Includes formatting for daily summaries and analytics.

Closes #42
```

```
fix(timer): correct overtime calculation rounding

Fixed issue where overtime was rounding incorrectly
for sessions less than 30 seconds.

Fixes #38
```

## Pull Request Process

### Before Submitting

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Run all tests** and ensure they pass
4. **Update CHANGELOG.md** with your changes
5. **Ensure code follows** style guidelines
6. **Rebase** on latest `main` branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings
```

### Review Process

1. At least one maintainer will review your PR
2. Address any requested changes
3. Once approved, a maintainer will merge your PR
4. Your contribution will be included in the next release

## Getting Help

- **Questions?** Open an issue with the `question` label
- **Stuck?** Comment on your issue or PR
- **Need clarification?** Ask in the issue discussion

## Recognition

All contributors will be recognized in the project documentation and release notes.

Thank you for contributing to Worklog Manager! 🎉
