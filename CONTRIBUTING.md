# Contributing to BIOTICA

First off, thank you for considering contributing to BIOTICA! We welcome contributions from biologists, bioinformaticians, software engineers, and anyone passionate about advancing biotechnology research.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Adding New Features](#adding-new-features)
- [Reporting Issues](#reporting-issues)
- [Contact](#contact)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to gitdeeper@gmail.com.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- PostgreSQL 13+ (optional, for database features)
- Basic knowledge of bioinformatics

### Setup Development Environment

```bash
# Fork the repository on GitLab, then clone your fork
git clone https://gitlab.com/YOUR_USERNAME/biotica.git
cd biotica

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
pre-commit install
```

Verify Setup

```bash
pytest tests/unit/ -v
ruff check biotica/
mypy biotica/
```

Development Workflow

1. Create an issue describing your proposed changes (unless it's a trivial fix)
2. Discuss with maintainers to ensure alignment
3. Fork and branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```
4. Make changes following our coding standards
5. Write/update tests for your changes
6. Run tests locally and ensure they pass
7. Commit with clear messages
8. Push to your fork
9. Open a Merge Request

Branch Naming

· feature/ - New features
· fix/ - Bug fixes
· docs/ - Documentation updates
· refactor/ - Code refactoring
· test/ - Test improvements
· perf/ - Performance optimizations

Pull Request Process

1. Update documentation for any changed functionality
2. Add tests for new features (coverage should not decrease)
3. Update CHANGELOG.md with your changes under "Unreleased"
4. Ensure CI passes (tests, linting, type checking)
5. Request review from maintainers
6. Address review feedback
7. Merge after approval and CI passes

PR Template

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #(issue number)

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Test update

## How Has This Been Tested?
Describe tests you added/ran

## Checklist
- [ ] Tests pass locally
- [ ] Docs updated
- [ ] CHANGELOG updated
- [ ] Code follows style guidelines
- [ ] Type hints added/updated
```

Coding Standards

Python

· Format: Black (line length 88)
· Imports: isort with black profile
· Linting: ruff (see pyproject.toml for rules)
· Type Hints: Required for all public functions
· Docstrings: Google style

Example

```python
"""Module description."""

from typing import Optional, Union

import numpy as np


def analyze_sequence(
    sequence: str,
    method: str = "basic",
    **kwargs
) -> dict:
    """Analyze biological sequence.
    
    Args:
        sequence: DNA/RNA/Protein sequence
        method: Analysis method (basic, advanced, ml)
        **kwargs: Additional parameters
    
    Returns:
        Analysis results dictionary
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not sequence:
        raise ValueError("Sequence cannot be empty")
    
    # Implementation
    result = {}
    
    return result
```

Testing Guidelines

Test Structure

```
tests/
├── conftest.py              # Fixtures
├── unit/                    # Unit tests
│   ├── test_analyze.py
│   ├── test_io.py
│   └── ...
├── integration/             # Integration tests
│   ├── test_pipeline.py
│   └── test_api.py
└── fixtures/                # Test data
    ├── sample_sequences.fasta
    └── sample_data.csv
```

Writing Tests

```python
import pytest
from biotica.analyze import sequence_analyzer

def test_sequence_analysis(sample_dna_sequence):
    """Test sequence analysis with valid data."""
    result = sequence_analyzer(sample_dna_sequence)
    
    assert "gc_content" in result
    assert 0 <= result["gc_content"] <= 1
    assert "length" in result

@pytest.mark.parametrize("sequence,expected_gc", [
    ("ATCG", 0.5),
    ("GCGC", 1.0),
    ("AAAA", 0.0),
])
def test_gc_content(sequence, expected_gc):
    """Test GC content calculation."""
    result = sequence_analyzer(sequence)
    assert result["gc_content"] == expected_gc
```

Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=biotica --cov-report=html

# Specific test
pytest tests/unit/test_analyze.py::test_sequence_analysis -v
```

Documentation

Building Documentation

```bash
cd docs
make html  # or make latexpdf for PDF
```

Documentation Standards

· README.md: Project overview, quick start
· docs/: Detailed documentation
· docstrings: In-code documentation
· notebooks: Example notebooks

Adding New Features

If adding a new analysis feature:

1. Create module in biotica/analysis/
2. Add to biotica/analysis/init.py
3. Update documentation in docs/analysis/
4. Add tests in tests/unit/
5. Update CLI if applicable

Reporting Issues

Bug Reports

Include:

· Clear title and description
· Steps to reproduce
· Expected vs actual behavior
· Environment details (OS, Python version, package versions)
· Logs or screenshots

Feature Requests

Include:

· Use case description
· Expected behavior
· Potential implementation approach
· References to similar features

Contact

· Issues: GitLab Issues
· Discussions: GitLab Discussions
· Email: biotica-dev@googlegroups.com

---

Thank you for contributing to BIOTICA! 🧬
