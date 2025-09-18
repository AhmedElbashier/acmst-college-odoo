# Contributing to ACMST College Odoo Management System

Thank you for your interest in contributing to the ACMST College Odoo Management System! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Check if the issue is already fixed** in the latest version
3. **Use the issue template** provided

When creating an issue, include:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (Odoo version, browser, OS)
- **Screenshots** if applicable

### Suggesting Enhancements

For feature requests:

1. **Check existing feature requests** first
2. **Provide clear use cases** and benefits
3. **Consider the scope** and complexity
4. **Explain the target audience**

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/acmst-college-odoo.git
   cd acmst-college-odoo
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Set up development environment**:
   ```bash
   # Using Docker (recommended)
   docker-compose up -d
   
   # Or set up Odoo manually
   ```

#### Development Guidelines

##### Code Style

- **Follow PEP 8** for Python code
- **Use meaningful variable names**
- **Add docstrings** for all functions and classes
- **Keep functions small** and focused
- **Use type hints** where appropriate

##### Odoo Best Practices

- **Follow Odoo's coding standards**
- **Use proper model inheritance**
- **Implement proper security rules**
- **Add comprehensive tests**
- **Use proper field types and constraints**

##### Commit Messages

Use clear, descriptive commit messages:

```
feat: add batch creation wizard for multiple batch creation
fix: resolve university search issue in college form
docs: update README with installation instructions
test: add unit tests for batch model validation
refactor: improve code organization in wizard module
```

##### Pull Request Process

1. **Ensure your code works** and passes all tests
2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Update CHANGELOG.md** if applicable
5. **Create a pull request** with a clear description

#### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🏗️ Development Setup

### Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+**
- **Odoo 17.0+**
- **Docker** (optional but recommended)

### Local Development

1. **Clone the repository**
2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Odoo**:
   ```bash
   # Configure Odoo
   cp config/odoo.conf.example config/odoo.conf
   # Edit config/odoo.conf with your settings
   ```

5. **Run Odoo**:
   ```bash
   python odoo-bin -c config/odoo.conf
   ```

### Docker Development

1. **Start services**:
   ```bash
   docker-compose up -d
   ```

2. **Access Odoo**:
   - Web interface: http://localhost:8069
   - Database: localhost:5432

## 🧪 Testing

### Running Tests

```bash
# All tests
python -m pytest addons/acmst_core_settings/tests/

# Specific test file
python -m pytest addons/acmst_core_settings/tests/test_batch.py

# With coverage
python -m pytest --cov=addons/acmst_core_settings addons/acmst_core_settings/tests/
```

### Test Guidelines

- **Write tests for new features**
- **Test edge cases and error conditions**
- **Maintain test coverage above 80%**
- **Use descriptive test names**
- **Mock external dependencies**

## 📝 Documentation

### Code Documentation

- **Add docstrings** to all functions and classes
- **Use type hints** for better code clarity
- **Comment complex logic**
- **Update README** for new features

### API Documentation

- **Document all public methods**
- **Include parameter descriptions**
- **Provide usage examples**
- **Update API documentation** for changes

## 🐛 Bug Reports

When reporting bugs, include:

1. **Environment details**:
   - Odoo version
   - Python version
   - Operating system
   - Browser (for UI issues)

2. **Steps to reproduce**:
   - Clear, numbered steps
   - Expected vs actual results
   - Screenshots if applicable

3. **Error messages**:
   - Full error traceback
   - Log files if relevant

4. **Additional context**:
   - Workarounds if any
   - Related issues
   - Impact assessment

## 🚀 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated
- [ ] Release notes prepared
- [ ] Tag created

## 📋 Code Review Process

### For Contributors

1. **Self-review** your code before submitting
2. **Ensure tests pass** and coverage is adequate
3. **Follow coding standards**
4. **Respond to feedback** promptly
5. **Be open to suggestions**

### For Reviewers

1. **Be constructive** and helpful
2. **Focus on code quality** and functionality
3. **Check for security issues**
4. **Verify tests are adequate**
5. **Approve when ready**

## 🎯 Areas for Contribution

### High Priority

- **Student Management Module**
- **Faculty Management Module**
- **Course Management Module**
- **Examination System**
- **Fee Management**

### Medium Priority

- **Library Management**
- **Hostel Management**
- **Reporting and Analytics**
- **Mobile App Integration**
- **API Development**

### Low Priority

- **UI/UX Improvements**
- **Performance Optimizations**
- **Documentation Updates**
- **Test Coverage**
- **Code Refactoring**

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: ahmedelbashier.2@gmail.com
- **Documentation**: Check the README and code comments

## 📜 License

By contributing, you agree that your contributions will be licensed under the LGPL-3 License.

## 🙏 Recognition

Contributors will be recognized in:

- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for contributing to the ACMST College Odoo Management System! 🎉
