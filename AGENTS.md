# AGENTS.md - Agentic Coding Guidelines

TalkingLLMs facilitates conversations between multiple LLM agents using the OpenRouter API.

## Build, Lint, and Test Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run main application
python main.py

# Run tests (uses unittest)
python -m unittest discover -s tests -v

# Run a single test file
python -m unittest tests.test_agent -v

# Run a single test function
python -m unittest tests.test_agent.TestAgent.test_agent_creation_with_type -v
```

## Code Style Guidelines

### General Principles
- Follow PEP 8 style guide for Python
- Keep functions small and focused (under 50 lines)
- Use meaningful variable and function names

### Imports
Order: standard library → third-party → local. Sort alphabetically within groups.

```python
import json
import os
from typing import Optional

import requests

from talkingllms.agent import Agent
from talkingllms.message import Message
```

- Avoid wildcard imports (`from module import *`)
- Use `isort` for automatic import sorting

### Formatting
- Use **Black** with default settings (line length 88)
- Use single quotes for strings unless double quotes are needed
- Add trailing commas in multi-line collections
- Use f-strings for string formatting

### Types
- Use type hints for all function signatures
- Prefer `typing` module types (`List`, `Dict`, `Optional`)
- Add type hints to class attributes in `__init__`

```python
class Agent:
    def __init__(self, model: str, api_key: str, temperature: float = 1.0) -> None:
        self.model: str = model
        self.messages: list[Message] = []
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `Agent`, `Message`)
- **Functions/variables**: `snake_case` (e.g., `get_messages()`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TOKENS`)
- **Private methods**: Prefix with underscore (e.g., `_internal_method`)

### Docstrings
Use Google-style docstrings for all public functions and classes:

```python
def load_file(file_path: str) -> str:
    """Load and return the contents of a text file.

    Args:
        file_path: Path to the file to read.

    Returns:
        The contents of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
```

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Handle exceptions at the appropriate level
- Never use bare `except:` - catch specific exceptions

```python
# Good
try:
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
except requests.RequestException as e:
    raise APIError(f"Request failed: {e}") from e

# Bad
try:
    return response.json()
except:
    return None
```

### Class Structure
- One public class per file is preferred
- Use `__init__.py` for package initialization
- Keep related functionality together

```python
class Agent:
    """Represents an LLM agent with conversation capabilities."""

    VALID_AGENTS = ["Canvas", "Sentinel", "SeniorSoftwareArchitect"]

    def __init__(
        self,
        model: str = "openrouter/pony-alpha",
        typeOfAgent: str = "",
        api_key: str = "",
        temperature: float = 1.0,
        system_prompt: str = "",
    ) -> None:
        """Initialize the agent."""
        if typeOfAgent not in self.VALID_AGENTS and not system_prompt:
            raise ValueError(f"Invalid agent type. Must be one of: {self.VALID_AGENTS}")
        self.typeOfAgent = typeOfAgent
        self.system_prompt = system_prompt
```

### Git Conventions
- Write descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Run `ruff check .` before committing to catch common issues

### Additional Recommendations
- Use dataclasses for simple data containers
- Use enums for fixed sets of values
- Keep dependency list minimal
- Add comments only when code is not self-explanatory