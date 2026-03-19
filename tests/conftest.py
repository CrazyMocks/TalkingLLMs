"""Pytest configuration and fixtures."""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_message():
    """Create a sample Message object."""
    from message import Message

    return Message("user", "Hello, world!")


@pytest.fixture
def mock_agent():
    """Create a mock Agent object."""
    agent = Mock()
    agent.typeOfAgent = "TestAgent"
    agent.system_prompt = "You are a test agent."
    agent.messages = []
    return agent


@pytest.fixture
def mock_openrouter_response():
    """Sample OpenRouter API response."""
    return {"choices": [{"message": {"content": "This is a test response."}}]}


@pytest.fixture
def sample_config_file(temp_dir):
    """Create a sample config file."""
    config_content = """# Sample config
name1: Alice
name2: Bob
model1: model1
model2: model2
system1: You are Alice.
system2: You are Bob.
init: Hello!
messages: 5
"""
    config_path = temp_dir / "test_config.txt"
    config_path.write_text(config_content)
    return config_path
