# AGENTS.md - Agentic Coding Guidelines

This document provides guidelines for agents operating in this repository.

## Project Overview

TalkingLLMs is a Python application that facilitates conversations between multiple LLM agents (Canvas, Sentinel, SeniorSoftwareArchitect, SeniorSoftwareDeveloper, TechLead, CodeScout, Meta). It uses the OpenRouter API to interact with various language models.

## Build, Lint, and Test Commands

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run main application (if applicable)
python main.py
```

### Testing

This project currently has **no test suite**. When adding tests:

```bash
# Run all tests with pytest
pytest

# Run a single test file
pytest tests/test_agent.py

# Run a single test function
pytest tests/test_agent.py::test_agent_initialization -v

# Run tests matching a pattern
pytest -k "test_agent"
```

### Linting and Formatting

This project currently has **no linting or formatting configuration**. The following are recommended standards:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with ruff
ruff check .

# Run all checks
ruff check . && black . --check && isort . --check
```

## Code Style Guidelines

### General Principles

- Follow PEP 8 style guide for Python
- Keep functions small and focused (under 50 lines when possible)
- Use meaningful variable and function names
- Write docstrings for all public functions and classes

### Imports

```python
# Standard library first, then third-party, then local
import json
import os
import re
from typing import Optional

import requests

from agent import Agent
from conversation import ConversationBtwAgents
from message import Message
from utils import load_file
```

- Use explicit relative imports for local modules
- Sort imports alphabetically within each group
- Use `isort` for automatic import sorting
- Avoid wildcard imports (`from module import *`)

### Formatting

- Use **Black** with default settings (line length 88)
- Use single quotes for strings unless double quotes are needed
- Add trailing commas in multi-line collections
- Use f-strings for string formatting
- Use type hints for function parameters and return values

```python
# Good
def process_message(content: str, role: str = "user") -> Message:
    """Create a new message with the given content and role."""
    return Message(role=role, content=content)


# Bad
def process_message(content, role="user"):
    return Message(role, content)
```

### Types

- Use type hints for all function signatures
- Prefer built-in types from `typing` module (`List`, `Dict`, `Optional`, `Union`)
- Use `Any` sparingly - prefer specific types when possible
- Add type hints to class attributes in `__init__`

```python
from typing import Optional


class Agent:
    def __init__(self, model: str, api_key: str, temperature: float = 1.0) -> None:
        self.model: str = model
        self.api_key: str = api_key
        self.temperature: float = temperature
        self.messages: list[Message] = []
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `Agent`, `Message`, `ConversationBtwAgents`)
- **Functions/variables**: `snake_case` (e.g., `get_messages()`, `api_key`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TOKENS`, `DEFAULT_MODEL`)
- **Private methods/attributes**: Prefix with underscore (e.g., `_internal_method`)

```python
# Good
class Message:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content

    def get_content(self) -> str:
        return self.content


# Bad - inconsistent naming
class message:
    def __init__(self, Role, Content):
        self.Role = Role
        self.Content = Content

    def GetContent(self):
        return self.Content
```

### Docstrings

Use Google-style or NumPy-style docstrings:

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
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
```

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Handle exceptions at the appropriate level
- Log errors before re-raising when appropriate

```python
# Good
def request(self) -> str:
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise APIError(f"Failed to get response: {e}") from e
    except KeyError as e:
        logger.error(f"Unexpected response format: {response.text}")
        raise APIError("Invalid response format") from e


# Bad
def request(self):
    try:
        # ... request logic
        return content
    except:
        return None
```

### Class Structure

```python
class Agent:
    """Represents an LLM agent with conversation capabilities."""

    VALID_AGENTS = ["Canvas", "Sentinel", "SeniorSoftwareArchitect"]

    def __init__(
        self,
        model: str = "openrouter/pony-alpha",
        agent_type: str = "",
        api_key: str = "",
        temperature: float = 1.0,
        system_prompt: str = "",
    ) -> None:
        """Initialize the agent.

        Args:
            model: The model identifier to use.
            agent_type: Type of agent (must be in VALID_AGENTS).
            api_key: API key for authentication.
            temperature: Sampling temperature (0.0 to 2.0).
            system_prompt: Custom system prompt.
        """
        if agent_type not in self.VALID_AGENTS and not system_prompt:
            raise ValueError(f"Invalid agent type. Must be one of: {self.VALID_AGENTS}")
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.messages: list[Message] = [Message("system", self.system_prompt)]

    def add_message(self, content: str, role: str = "user") -> None:
        """Add a message to the conversation history."""
        self.messages.append(Message(role, content))
```

### File Organization

- One public class per file is preferred
- Private helper functions can be grouped in `utils.py` or a dedicated module
- Keep related functionality together
- Use `__init__.py` for package initialization

### Git Conventions

- Write descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issues in commit messages when applicable

### Additional Recommendations

- Use dataclasses for simple data containers
- Use enums for fixed sets of values
- Keep dependency list minimal
- Add comments only when code is not self-explanatory
- Run `ruff check .` before committing to catch common issues
