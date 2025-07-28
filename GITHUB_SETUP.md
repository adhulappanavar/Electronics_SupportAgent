# GitHub Setup Guide for Electronics_SupportAgent 🚀

This guide will help you set up the Electronics_SupportAgent project on GitHub and prepare it for collaboration.

## 📋 Prerequisites

- GitHub account
- Git installed on your local machine
- SSH key configured (recommended) or GitHub CLI

## 🎯 Quick Setup

### 1. Create GitHub Repository

#### Option A: Using GitHub Web Interface
1. Go to [GitHub.com](https://github.com)
2. Click the "+" icon in the top right
3. Select "New repository"
4. Fill in the details:
   - **Repository name**: `Electronics_SupportAgent`
   - **Description**: `Intelligent RAG system for electronics support using LanceDB, Cognee, and n8n`
   - **Visibility**: Choose Public or Private
   - **Initialize with**: Don't initialize (we'll push existing code)
5. Click "Create repository"

#### Option B: Using GitHub CLI
```bash
# Install GitHub CLI if not installed
# macOS: brew install gh
# Ubuntu: sudo apt install gh

# Login to GitHub
gh auth login

# Create repository
gh repo create Electronics_SupportAgent \
  --description "Intelligent RAG system for electronics support using LanceDB, Cognee, and n8n" \
  --public \
  --source=. \
  --remote=origin \
  --push
```

### 2. Add Remote and Push

```bash
# Add the remote repository
git remote add origin https://github.com/yourusername/Electronics_SupportAgent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Verify Setup

```bash
# Check remote configuration
git remote -v

# Should show:
# origin  https://github.com/yourusername/Electronics_SupportAgent.git (fetch)
# origin  https://github.com/yourusername/Electronics_SupportAgent.git (push)
```

## 🔧 Repository Configuration

### 1. Repository Settings

Go to your repository on GitHub and configure:

#### General Settings
- **Repository name**: `Electronics_SupportAgent`
- **Description**: `Intelligent RAG system for electronics support using LanceDB, Cognee, and n8n`
- **Topics**: Add relevant tags like `rag`, `lancedb`, `cognee`, `n8n`, `ai`, `electronics-support`

#### Security Settings
- **Dependency graph**: Enable
- **Dependabot alerts**: Enable
- **Code scanning**: Enable (if using GitHub Advanced Security)

### 2. Branch Protection

Set up branch protection for `main`:
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date
   - Include administrators

### 3. Issue Templates

Create issue templates for better organization:

#### Bug Report Template
Create `.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. macOS 14.0]
 - Python Version: [e.g. 3.12.2]
 - Package Versions: [e.g. lancedb==0.4.0]

**Additional context**
Add any other context about the problem here.
```

#### Feature Request Template
Create `.github/ISSUE_TEMPLATE/feature_request.md`:
```markdown
---
name: Feature request
about: Suggest an idea for this project
title: ''
labels: enhancement
assignees: ''

---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

### 4. Pull Request Template

Create `.github/pull_request_template.md`:
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## 🚀 GitHub Actions Setup

### 1. Create Workflow Directory

```bash
mkdir -p .github/workflows
```

### 2. Python CI/CD Workflow

Create `.github/workflows/python-ci.yml`:
```yaml
name: Python CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### 3. Security Scanning

Create `.github/workflows/security.yml`:
```yaml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Bandit Security Linter
      run: |
        pip install bandit
        bandit -r . -f json -o bandit-report.json || true
    
    - name: Run Safety Check
      run: |
        pip install safety
        safety check --json --output safety-report.json || true
```

## 📊 GitHub Pages Setup

### 1. Enable GitHub Pages

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`
4. Folder: `/docs`
5. Save

### 2. Create Documentation

Create `docs/index.md`:
```markdown
# Electronics_SupportAgent Documentation

Welcome to the Electronics_SupportAgent documentation.

## Quick Start

1. Clone the repository
2. Install dependencies
3. Configure environment
4. Run the application

## Features

- RAG-based knowledge retrieval
- AI-powered response generation
- Continuous learning system
- n8n workflow integration

## API Reference

See the [API Documentation](api.md) for detailed endpoint information.
```

## 🔐 Security Best Practices

### 1. Secrets Management

Add repository secrets for sensitive data:
1. Go to Settings → Secrets and variables → Actions
2. Add secrets:
   - `OPENAI_API_KEY`
   - `COGNEE_API_KEY`
   - `TEST_DATABASE_URL`

### 2. Dependabot Configuration

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "yourusername"
    assignees:
      - "yourusername"
```

## 📈 Analytics and Insights

### 1. Enable Repository Insights

- Go to Settings → General
- Enable "Features" section options:
  - Wikis
  - Issues
  - Projects
  - Discussions

### 2. Set Up Project Board

1. Go to Projects tab
2. Create new project
3. Add columns: Backlog, In Progress, Review, Done
4. Add automation rules

## 🎯 Next Steps

### 1. First Release

```bash
# Create a release tag
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# Create GitHub release
gh release create v1.0.0 --title "Initial Release" --notes "First stable release of Electronics_SupportAgent"
```

### 2. Community Setup

- Enable Discussions
- Set up community health files
- Create contributing guidelines
- Add code of conduct

### 3. Documentation

- Set up GitHub Pages
- Create comprehensive README
- Add API documentation
- Create user guides

## 🔧 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Check SSH key setup
ssh -T git@github.com

# Or use HTTPS with token
git remote set-url origin https://yourusername:token@github.com/yourusername/Electronics_SupportAgent.git
```

#### Large File Issues
```bash
# If you have large files that shouldn't be tracked
git rm --cached large_file.db
git commit -m "Remove large file from tracking"
```

#### Branch Protection Issues
- Ensure you have proper permissions
- Check if branch protection is too restrictive
- Verify required status checks are passing

## 📞 Support

If you encounter issues:

1. Check the [GitHub Help](https://help.github.com/)
2. Review the [GitHub CLI documentation](https://cli.github.com/)
3. Search existing issues in the repository
4. Create a new issue with detailed information

---

**Your Electronics_SupportAgent repository is now ready for collaboration! 🎉** 