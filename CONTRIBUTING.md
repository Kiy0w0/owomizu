# 🤝 Contributing to Mizu OwO

<div align="center">

![Mizu OwO](static/imgs/mizu.png)

**Welcome to the Mizu OwO Community!**

[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/bkvMhwjSPG)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/kiy0w0/owomizu)

*Thank you for your interest in contributing to Mizu OwO! 水*

</div>

---

## 📋 Table of Contents

- [🌟 How to Contribute](#-how-to-contribute)
- [🐛 Bug Reports](#-bug-reports)
- [💡 Feature Requests](#-feature-requests)
- [💻 Code Contributions](#-code-contributions)
- [📖 Documentation](#-documentation)
- [🔧 Development Setup](#-development-setup)
- [📏 Coding Standards](#-coding-standards)
- [🧪 Testing](#-testing)
- [📦 Pull Request Process](#-pull-request-process)
- [👥 Community Guidelines](#-community-guidelines)
- [🏆 Recognition](#-recognition)

---

## 🌟 How to Contribute

There are many ways to contribute to Mizu OwO, and we welcome all types of contributions:

### 🎯 Quick Contribution Options

| Type | Description | Skill Level |
|------|-------------|-------------|
| 🐛 **Bug Reports** | Report issues you encounter | Beginner |
| 💡 **Feature Ideas** | Suggest new features | Beginner |
| 📖 **Documentation** | Improve guides and docs | Beginner |
| 🌐 **Translations** | Translate to other languages | Beginner |
| 💻 **Code** | Fix bugs or add features | Intermediate |
| 🧪 **Testing** | Test new features | Intermediate |
| 🔒 **Security** | Find security vulnerabilities | Advanced |

---

## 🐛 Bug Reports

### Before Reporting
1. **Check existing issues** on [GitHub Issues](https://github.com/kiy0w0/owomizu/issues)
2. **Update to latest version** using `python updater.py`
3. **Test in clean environment** (fresh install)

### How to Report

#### Use our Bug Report Template:
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
- OS: [e.g. Windows 11, Ubuntu 22.04, Termux]
- Python Version: [e.g. 3.9.7]
- Bot Version: [run `git log --oneline -1`]

**Screenshots/Logs**
Add screenshots or paste error logs here.

**Additional Context**
Any other context about the problem.
```

### 🚨 Critical Bugs (Security/Data Loss)
- **Email directly**: security@mizunetwork.dev
- **Don't post publicly** until fixed
- **Include detailed reproduction steps**

---

## 💡 Feature Requests

### Before Requesting
1. **Search existing requests** in [GitHub Issues](https://github.com/kiy0w0/owomizu/issues?q=is%3Aissue+label%3Aenhancement)
2. **Join Discord** to discuss with community
3. **Consider if it fits** Mizu OwO's scope

### Feature Request Template:
```markdown
**Feature Summary**
Brief description of the feature.

**Problem Statement**
What problem does this solve?

**Proposed Solution**
Detailed description of your proposed feature.

**Alternatives Considered**
Other solutions you've considered.

**Use Cases**
Who would use this and how?

**Implementation Ideas**
Technical suggestions (optional).

**Priority**
Low / Medium / High - How important is this?
```

### 🎯 Feature Categories We Love
- **Automation Improvements** - Better farming efficiency
- **Safety Features** - Anti-detection, account protection
- **User Experience** - Dashboard improvements, easier setup
- **Performance** - Speed optimizations, resource usage
- **Platform Support** - New OS support, mobile compatibility

---

## 💻 Code Contributions

### 🔧 Development Workflow

#### 1. Fork & Clone
```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/owomizu.git
cd owomizu
git remote add upstream https://github.com/kiy0w0/owomizu.git
```

#### 2. Create Feature Branch
```bash
# Create branch for your feature
git checkout -b feature/amazing-new-feature

# Or for bug fixes
git checkout -b fix/bug-description
```

#### 3. Make Changes
- Follow our [coding standards](#-coding-standards)
- Write tests for new features
- Update documentation if needed

#### 4. Test Your Changes
```bash
# Run the bot locally
python mizu.py

# Test specific features
python -m pytest tests/

# Check code style
flake8 .
black --check .
```

#### 5. Commit & Push
```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add amazing new feature

- Adds X functionality
- Improves Y performance
- Fixes Z issue"

# Push to your fork
git push origin feature/amazing-new-feature
```

#### 6. Create Pull Request
- Go to GitHub and create PR
- Use our PR template
- Link related issues
- Request review

### 🎯 Areas We Need Help

#### High Priority
- 🔒 **Security improvements**
- 🚀 **Performance optimizations**
- 🐛 **Bug fixes**
- 📱 **Mobile platform support**

#### Medium Priority
- 🎨 **Dashboard UI improvements**
- 📊 **Analytics features**
- 🌐 **Internationalization**
- 🧪 **Test coverage**

#### Low Priority
- 📖 **Documentation**
- 🎵 **Fun features**
- 🎨 **Themes/customization**

---

## 📖 Documentation

### Types of Documentation
- **User Guides** - Help users set up and use the bot
- **API Documentation** - Code documentation
- **Tutorials** - Step-by-step guides
- **FAQ** - Common questions and answers

### Documentation Standards
- **Clear and concise** writing
- **Step-by-step instructions** with screenshots
- **Code examples** with proper syntax highlighting
- **Keep updated** with latest features

### How to Contribute Docs
1. **Identify gaps** in existing documentation
2. **Create or improve** markdown files
3. **Test instructions** on clean environment
4. **Submit PR** with documentation changes

---
---

## 🔧 Development Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# Git
git --version

# Node.js (for frontend development)
node --version
npm --version
```

### Local Development
```bash
# Clone repository
git clone https://github.com/kiy0w0/owomizu.git
cd owomizu

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Set up configuration
cp config/settings.example.json config/settings.json
# Edit config files as needed

# Run the bot
python mizu.py
```

### Development Tools
```bash
# Code formatting
black .
isort .

# Linting
flake8 .
pylint mizu.py

# Type checking
mypy .

# Testing
pytest

# Security scanning
bandit -r .
```

---

## 📏 Coding Standards

### Python Style Guide
We follow **PEP 8** with some modifications:

#### Code Formatting
```python
# Use Black for formatting
# Line length: 88 characters
# Use double quotes for strings
# Use type hints where possible

def process_message(message: str, user_id: int) -> bool:
    """Process a Discord message.
    
    Args:
        message: The message content
        user_id: Discord user ID
        
    Returns:
        True if processed successfully
    """
    if not message or not user_id:
        return False
    
    # Process message logic here
    return True
```

#### Naming Conventions
```python
# Variables and functions: snake_case
user_name = "example"
def get_user_data():
    pass

# Classes: PascalCase
class MessageHandler:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private methods: _leading_underscore
def _internal_method(self):
    pass
```

#### Documentation
```python
# Use docstrings for all public functions/classes
# Follow Google style docstrings

def calculate_cooldown(command: str, user_level: int) -> float:
    """Calculate command cooldown based on user level.
    
    Args:
        command: Command name (e.g., "hunt", "battle")
        user_level: User's current level
        
    Returns:
        Cooldown in seconds
        
    Raises:
        ValueError: If command is invalid
        
    Example:
        >>> calculate_cooldown("hunt", 50)
        15.5
    """
    pass
```

### JavaScript Style Guide
```javascript
// Use modern ES6+ syntax
// Use const/let instead of var
// Use arrow functions where appropriate

const processCommand = async (command) => {
    try {
        const result = await api.sendCommand(command);
        return result.success;
    } catch (error) {
        console.error('Command failed:', error);
        return false;
    }
};
```

### CSS Style Guide
```css
/* Use BEM naming convention */
/* Organize by component */
/* Use CSS custom properties for theming */

.dashboard__header {
    background: var(--primary-color);
    padding: 1rem;
}

.dashboard__button {
    background: var(--accent-color);
    border: none;
    border-radius: 0.25rem;
    padding: 0.5rem 1rem;
}

.dashboard__button--primary {
    background: var(--primary-color);
    color: white;
}
```

---

## 🧪 Testing

### Test Types
- **Unit Tests** - Individual function testing
- **Integration Tests** - Component interaction testing
- **End-to-End Tests** - Full workflow testing
- **Performance Tests** - Speed and resource usage

### Writing Tests
```python
import pytest
from mizu import MessageHandler

class TestMessageHandler:
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = MessageHandler()
    
    def test_process_hunt_command(self):
        """Test hunt command processing."""
        result = self.handler.process("owo hunt")
        assert result.success is True
        assert "hunt" in result.command_type
    
    @pytest.mark.asyncio
    async def test_async_command_processing(self):
        """Test async command processing."""
        result = await self.handler.process_async("owo battle")
        assert result is not None
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_commands.py

# Run with coverage
pytest --cov=mizu

# Run performance tests
pytest tests/performance/
```

---

## 📦 Pull Request Process

### PR Checklist
- [ ] **Branch naming**: `feature/description` or `fix/description`
- [ ] **Descriptive title** and detailed description
- [ ] **Link related issues** using "Closes #123"
- [ ] **Tests added/updated** for new functionality
- [ ] **Documentation updated** if needed
- [ ] **Code follows style guidelines**
- [ ] **No breaking changes** (or clearly documented)
- [ ] **Tested locally** on multiple platforms if possible

### PR Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Closes #123
Related to #456

## Testing
- [ ] Tested locally
- [ ] Added/updated unit tests
- [ ] Tested on multiple platforms

## Screenshots (if applicable)
Add screenshots here.

## Additional Notes
Any additional information or context.
```

### Review Process
1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** on different platforms
4. **Documentation review**
5. **Approval and merge**

### After Merge
- **Update changelog** if significant
- **Close related issues**
- **Announce in Discord** if major feature
- **Update documentation** if needed

---

## 👥 Community Guidelines

### Code of Conduct
We are committed to providing a welcoming and inclusive environment for all contributors.

#### Our Standards
- **Be respectful** and inclusive
- **Be collaborative** and helpful
- **Be patient** with newcomers
- **Give constructive feedback**
- **Accept criticism gracefully**

#### Unacceptable Behavior
- **Harassment** or discrimination
- **Trolling** or insulting comments
- **Personal attacks**
- **Publishing private information**
- **Spam** or off-topic content

#### Enforcement
- **First violation**: Warning
- **Second violation**: Temporary ban
- **Serious violations**: Permanent ban

### Communication Channels

#### Discord Server
- **General discussion**: #general
- **Development**: #development
- **Bug reports**: #bug-reports
- **Feature requests**: #feature-requests
- **Help & support**: #help

#### GitHub
- **Issues**: Bug reports and feature requests
- **Discussions**: General project discussion
- **Pull Requests**: Code contributions

#### Email
- **Security issues**: security@mizunetwork.dev
- **General inquiries**: contact@mizunetwork.dev

---

## 🏆 Recognition

### Contributor Levels

#### 🌱 **New Contributor**
- First contribution to the project
- Welcome package and Discord role

#### 🚀 **Active Contributor**
- 5+ merged contributions
- Special Discord role and privileges
- Name in contributors list

#### ⭐ **Core Contributor**
- 20+ merged contributions
- Repository write access
- Involved in project decisions

#### 💎 **Maintainer**
- Long-term project commitment
- Full repository access
- Project leadership responsibilities

### Recognition Methods
- **Contributors page** on website
- **Discord roles** and special privileges
- **GitHub achievements** and badges
- **Social media shoutouts**
- **Annual contributor awards**

### Hall of Fame
Special recognition for outstanding contributions:
- **Most helpful contributor**
- **Best bug finder**
- **Documentation champion**
- **Community builder**
- **Innovation award**

---

## 📞 Getting Help

### For Contributors

#### Development Questions
- **Discord #development** - Quick questions
- **GitHub Discussions** - Detailed technical discussions
- **Code review comments** - Specific code questions

#### Getting Started
- **Discord #newcomers** - New contributor welcome
- **Mentorship program** - Paired with experienced contributor
- **Good first issues** - Beginner-friendly tasks

#### Resources
- **Development docs** - Technical documentation
- **Code examples** - Sample implementations
- **Video tutorials** - Visual learning resources

---

## 🎯 Quick Start for Contributors

### I want to report a bug
1. Check [existing issues](https://github.com/kiy0w0/owomizu/issues)
2. Create new issue with bug template
3. Provide detailed reproduction steps

### I want to suggest a feature
1. Join [Discord](https://discord.gg/bkvMhwjSPG) to discuss
2. Create GitHub issue with feature template
3. Participate in community discussion

### I want to contribute code
1. Fork repository
2. Create feature branch
3. Make changes following style guide
4. Write tests
5. Submit pull request

### I want to improve documentation
1. Identify documentation gaps
2. Create/edit markdown files
3. Test instructions work
4. Submit pull request

### I want to help with design
1. Join Discord #design channel
2. Review current UI/UX
3. Create mockups or improvements
4. Submit design proposals

---

<div align="center">

## 🌊 Thank You for Contributing! 

**Mizu Dayo**

*水*

[![Contributors](https://img.shields.io/github/contributors/kiy0w0/owomizu?style=for-the-badge)](https://github.com/kiy0w0/owomizu/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/kiy0w0/owomizu?style=for-the-badge)](https://github.com/kiy0w0/owomizu/stargazers)
[![Forks](https://img.shields.io/github/forks/kiy0w0/owomizu?style=for-the-badge)](https://github.com/kiy0w0/owomizu/network/members)

</div>
