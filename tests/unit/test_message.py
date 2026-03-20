"""Tests for Message class."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from message import Message


class TestMessageCreation:
    """Tests for Message object creation."""

    def test_create_message_with_role_and_content(self):
        """Test creating a message with valid role and content."""
        msg = Message("user", "Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_create_message_with_different_roles(self):
        """Test creating messages with different valid roles."""
        user_msg = Message("user", "User message")
        assistant_msg = Message("assistant", "Assistant message")
        system_msg = Message("system", "System message")

        assert user_msg.role == "user"
        assert assistant_msg.role == "assistant"
        assert system_msg.role == "system"

    def test_create_empty_message(self):
        """Test creating a message with empty content."""
        msg = Message("user", "")
        assert msg.content == ""


class TestMessageToDict:
    """Tests for to_dict method."""

    def test_to_dict_returns_correct_format(self):
        """Test that to_dict returns correct dictionary format."""
        msg = Message("user", "Test content")
        result = msg.to_dict()
        assert result == {"role": "user", "content": "Test content"}

    def test_to_dict_with_empty_content(self):
        """Test to_dict with empty content."""
        msg = Message("assistant", "")
        result = msg.to_dict()
        assert result == {"role": "assistant", "content": ""}


class TestMessageGetters:
    """Tests for getter methods."""

    def test_get_role_returns_role(self):
        """Test get_role returns the role."""
        msg = Message("system", "Test")
        assert msg.get_role() == "system"

    def test_get_content_returns_content(self):
        """Test get_content returns the content."""
        msg = Message("user", "Hello world")
        assert msg.get_content() == "Hello world"


class TestMessageSetters:
    """Tests for setter methods."""

    def test_set_role_valid(self):
        """Test setting a valid role."""
        msg = Message("user", "Test")
        msg.set_role("assistant")
        assert msg.role == "assistant"

    def test_set_role_invalid_raises_error(self):
        """Test setting an invalid role raises ValueError."""
        msg = Message("user", "Test")
        with pytest.raises(ValueError) as exc_info:
            msg.set_role("invalid_role")
        assert "Invalid role" in str(exc_info.value)

    def test_set_role_all_valid_values(self):
        """Test setting all valid role values."""
        msg = Message("user", "Test")

        for role in ["user", "assistant", "system"]:
            msg.set_role(role)
            assert msg.role == role

    def test_set_content(self):
        """Test setting content."""
        msg = Message("user", "Original")
        msg.set_content("Updated")
        assert msg.content == "Updated"


class TestMessageRoleChecks:
    """Tests for role checking methods."""

    def test_is_user(self):
        """Test is_user method."""
        user_msg = Message("user", "Test")
        assert user_msg.is_user() is True
        assert user_msg.is_assistant() is False
        assert user_msg.is_system() is False

    def test_is_assistant(self):
        """Test is_assistant method."""
        assistant_msg = Message("assistant", "Test")
        assert assistant_msg.is_assistant() is True
        assert assistant_msg.is_user() is False
        assert assistant_msg.is_system() is False

    def test_is_system(self):
        """Test is_system method."""
        system_msg = Message("system", "Test")
        assert system_msg.is_system() is True
        assert system_msg.is_user() is False
        assert system_msg.is_assistant() is False


class TestMessageFlipRole:
    """Tests for flip_role method."""

    def test_flip_role_user_to_assistant(self):
        """Test flipping role from user to assistant."""
        msg = Message("user", "Test")
        msg.flip_role()
        assert msg.role == "assistant"

    def test_flip_role_assistant_to_user(self):
        """Test flipping role from assistant to user."""
        msg = Message("assistant", "Test")
        msg.flip_role()
        assert msg.role == "user"

    def test_flip_role_system_unchanged(self):
        """Test that system role remains unchanged when flipped."""
        msg = Message("system", "Test")
        msg.flip_role()
        assert msg.role == "system"

    def test_flip_role_multiple_times(self):
        """Test flipping role multiple times."""
        msg = Message("user", "Test")
        msg.flip_role()  # assistant
        msg.flip_role()  # user
        msg.flip_role()  # assistant
        assert msg.role == "assistant"


class TestMessageString:
    """Tests for __str__ method."""

    def test_str_representation(self):
        """Test string representation of message."""
        msg = Message("user", "Hello")
        assert str(msg) == "user: Hello"

    def test_str_with_empty_content(self):
        """Test string representation with empty content."""
        msg = Message("assistant", "")
        assert str(msg) == "assistant: "
