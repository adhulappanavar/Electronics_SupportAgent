# Contributing to Electronics_SupportAgent 🤝

Thank you for your interest in contributing to Electronics_SupportAgent! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### Types of Contributions

We welcome contributions in the following areas:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new features and improvements
- **📚 Documentation**: Improve documentation and examples
- **🧪 Testing**: Add tests and improve test coverage
- **🔧 Code Improvements**: Optimize performance and fix bugs
- **🎨 UI/UX**: Enhance the user interface and experience

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 20.19+ (for n8n features)
- Git
- A GitHub account

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/Electronics_SupportAgent.git
   cd Electronics_SupportAgent
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (if available)
   pip install -r requirements-dev.txt
   ```

4. **Configure Environment**
   ```bash
   # Copy example environment file
   cp env.example .env
   
   # Edit .env with your API keys
   nano .env
   ```

5. **Run Tests**
   ```bash
   # Run all tests
   python -m pytest tests/
   
   # Run specific test files
   python test_system.py
   python test_enhanced_features.py
   ```

## 📝 Development Guidelines

### Code Style

#### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints where appropriate
- Add docstrings for all functions and classes
- Keep functions focused and under 50 lines when possible

#### Example
```python
def process_document(file_path: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
    """
    Process a document and return chunks with metadata.
    
    Args:
        file_path: Path to the document file
        chunk_size: Size of each text chunk
        
    Returns:
        List of document chunks with metadata
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Process the document
    chunks = []
    # ... processing logic ...
    
    return chunks
```

### Git Workflow

1. **Create a Feature Branch**
   ```bash
   # Create and switch to a new branch
   git checkout -b feature/your-feature-name
   
   # Or for bug fixes
   git checkout -b fix/bug-description
   ```

2. **Make Your Changes**
   - Write your code
   - Add tests for new features
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   # Run the test suite
   python -m pytest tests/
   
   # Run linting
   flake8 .
   
   # Run type checking (if mypy is configured)
   mypy .
   ```

4. **Commit Your Changes**
   ```bash
   # Add your changes
   git add .
   
   # Commit with a descriptive message
   git commit -m "feat: add new document processor for PDF files"
   
   # Push to your fork
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the PR template
   - Submit the PR

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Examples
```bash
git commit -m "feat: add support for Excel file processing"
git commit -m "fix: resolve LanceDB schema validation error"
git commit -m "docs: update installation instructions"
git commit -m "test: add unit tests for document processor"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=.

# Run specific test file
python test_system.py

# Run tests in parallel
python -m pytest -n auto
```

### Writing Tests

- Write tests for all new features
- Aim for at least 80% code coverage
- Use descriptive test names
- Mock external dependencies

#### Example Test
```python
import pytest
from processors.document_processor import DocumentProcessor

class TestDocumentProcessor:
    def test_extract_text_from_pdf(self):
        """Test PDF text extraction."""
        processor = DocumentProcessor()
        result = processor.extract_text_from_file("tests/data/sample.pdf")
        assert result is not None
        assert len(result) > 0
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        processor = DocumentProcessor()
        text = "This is a test document with multiple sentences. " * 10
        chunks = processor.chunk_text(text, chunk_size=100)
        assert len(chunks) > 1
        assert all(len(chunk) <= 100 for chunk in chunks)
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Include type hints
- Provide examples for complex functions
- Document exceptions and edge cases

### User Documentation

- Update README.md for new features
- Add examples and use cases
- Include troubleshooting guides
- Keep installation instructions current

## 🔍 Code Review Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] No sensitive data is included
- [ ] Environment variables are properly handled

### Review Checklist

- [ ] Code is readable and well-documented
- [ ] Tests cover new functionality
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact is considered
- [ ] Security implications are addressed

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. macOS 14.0]
- Python Version: [e.g. 3.12.2]
- Package Versions: [e.g. lancedb==0.4.0]

**Additional Context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
How would this feature be used?

**Proposed Implementation**
Any ideas on how to implement this feature.

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
Any other context or screenshots.
```

## 🏷️ Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Changelog is updated
- [ ] Version is bumped
- [ ] Release notes are written
- [ ] Dependencies are updated

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the project's coding standards
- Respect maintainers' time and decisions

### Communication

- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for questions and general discussion
- Be clear and specific in your communications
- Provide context and examples when asking for help

## 🎉 Recognition

### Contributors

All contributors will be recognized in:
- The project README
- Release notes
- Contributor hall of fame

### Types of Recognition

- **Code Contributors**: Direct code contributions
- **Documentation Contributors**: Documentation improvements
- **Bug Reporters**: Valuable bug reports
- **Feature Requesters**: Useful feature suggestions
- **Reviewers**: Code review contributions

## 📞 Getting Help

### Questions and Support

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the README and docs folder
- **Code Examples**: Look at existing code and tests

### Mentorship

- New contributors are welcome to ask for help
- Maintainers are happy to guide you through the process
- Don't hesitate to ask questions or request clarification

## 🚀 Quick Start for Contributors

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/Electronics_SupportAgent.git
   cd Electronics_SupportAgent
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Make a Small Change**
   ```bash
   git checkout -b docs/update-readme
   # Make your changes
   git add .
   git commit -m "docs: update README with new information"
   git push origin docs/update-readme
   ```

4. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the template
   - Submit!

---

**Thank you for contributing to Electronics_SupportAgent! 🎉**

Your contributions help make this project better for everyone in the electronics support community. 