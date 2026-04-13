# Contributing to PolymarketAgent

Thank you for your interest in contributing! This is an **educational/test project**, and we welcome contributions that improve the codebase for learning purposes.

## ⚠️ Important Disclaimer

**Contributions to this project are for educational and testing purposes only.** This is not a production system and should not be used for real financial trading.

## Code of Conduct

Be respectful, inclusive, and constructive. We're here to learn together.

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/yourusername/PolymarketAgent.git
cd PolymarketAgent
git remote add upstream https://github.com/original/PolymarketAgent.git
```

### 2. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # (if exists)
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix-name
```

## Development Workflow

### Code Style

This project uses:

- **Black** - Code formatting (automatic)
- **Flake8** - Linting
- **MyPy** - Type checking

Format before committing:

```bash
black . --line-length 100
flake8 src/ tests/
mypy src/
```

### Testing

All code must pass tests:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py -v

# Run matching pattern
pytest -k "sentiment" -v
```

**Important:** Tests should pass before submitting a PR.

### Commit Messages

Use clear, descriptive commit messages:

```
✨ feat: Add new Claude tool for market sentiment

- Extracts sentiment from news articles
- Integrates with decision engine
- Includes unit tests and documentation
```

Format:
- Use prefix: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- First line: under 50 characters
- Body: explain *what* and *why*, not *how*

## Pull Request Process

1. **Update from upstream** before submitting:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create descriptive PR title:**
   ```
   [Feature] Add arbitrage detector tool
   ```

3. **In PR description, include:**
   - What problem does this solve?
   - How does it work?
   - How can reviewers test it?
   - Any breaking changes?

4. **Ensure CI passes:**
   - All tests pass (`pytest`)
   - Code is formatted (`black`)
   - Lint passes (`flake8`)
   - Types pass (`mypy`)

5. **Request review** from maintainers

6. **Address feedback** - iterate with reviewers

7. **Merge** once approved

## What to Contribute

### Good Issues for Beginners

- 🟢 Tests (expanding test coverage)
- 🟢 Documentation (clearer docs, examples)
- 🟢 Bug fixes (small, isolated)
- 🟢 Refactoring (improving existing code)

### Examples

**Add a unit test:**
```python
# tests/unit/test_sentiment_analyzer.py
def test_sentiment_analyzer_positive_text():
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("Bitcoin is amazing!")
    assert result["sentiment"] > 0.5
```

**Improve documentation:**
```markdown
- Clarify existing docs/API_REFERENCE.md
- Add examples for Claude tools
- Explain architecture decisions
```

**Fix a bug:**
```python
# Find issue, write test that fails, fix code, test passes
# Include regression test so bug doesn't return
```

## Areas for Contribution

### High Priority

- 📊 **Data collectors:** Expand FiveThirtyEight, ESPN, NewsAPI
- 🧠 **Claude tools:** New decision-making tools
- 📈 **Performance tracking:** Better metrics & visualization
- 🧪 **Tests:** More unit & integration tests

### Medium Priority

- 📝 **Documentation:** Architecture docs, examples
- 🔧 **Configuration:** Better config management
- 🐛 **Bug fixes:** Reported issues
- ⚡ **Performance:** Optimize slow code paths

### Lower Priority

- 🎨 **UI/Dashboard:** Visualization (not focus)
- 📦 **Packaging:** PyPI distribution
- 🔄 **CI/CD:** GitHub Actions workflows

## Development Tips

### Debugging

```python
# Add temporary logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {variable}")

# Or use print (remove before committing)
print("DEBUG:", variable)
```

### Running a Single Test

```bash
pytest tests/unit/test_agents.py::test_specific_function -v
```

### Checking Coverage

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Interactive Testing

```bash
python -i -c "from src.agents.claude_agent import ClaudeAgent; agent = ClaudeAgent()"
# Now you have `agent` available in Python shell
```

## Documentation

All code should be documented:

```python
def calculate_kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Calculate optimal position sizing using Kelly Criterion.
    
    Args:
        win_rate: Fraction of winning trades (0.0 to 1.0)
        avg_win: Average winning trade profit
        avg_loss: Average losing trade loss (positive value)
    
    Returns:
        Kelly fraction as decimal (e.g., 0.025 = 2.5% of balance)
    
    Example:
        >>> calculate_kelly_fraction(0.6, 1.5, 1.0)
        0.25
    """
    return (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
```

## Reporting Issues

Found a bug? Have a suggestion?

1. Check existing issues first
2. Create descriptive issue title
3. Include:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs. actual behavior
   - Your environment (OS, Python version)
   - Relevant code/logs

## Community

- 📧 Questions? Open an issue
- 💬 Discussions? Use GitHub Discussions
- 🐦 Updates? Follow the project

## License

All contributions must be compatible with the MIT License. By contributing, you agree your code will be published under MIT terms.

## Questions?

- Check existing documentation
- Review similar PRs/issues
- Ask in a new issue
- No question is too basic - we're here to help!

---

**Thank you for contributing to PolymarketAgent! 🚀**

Remember: This is educational software. Contributions should improve learning and code quality.
