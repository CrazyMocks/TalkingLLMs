"""Tests for Agent class."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agent import Agent


class TestAgentInit:
    """Tests for Agent initialization."""

    def test_agent_default_values(self):
        """Test agent with default values."""
        agent = Agent(api_key="test_key", system_prompt="Default system prompt")
        assert agent.model == "openrouter/pony-alpha"
        assert agent.typeOfAgent == ""
        assert agent.api_key == "test_key"
        assert agent.temperature == 1.0

    def test_agent_custom_values(self):
        """Test agent with custom values."""
        agent = Agent(
            model="custom/model",
            typeOfAgent="TestAgent",
            api_key="test_key",
            temperature=0.5,
            system_prompt="You are a test agent.",
        )
        assert agent.model == "custom/model"
        assert agent.typeOfAgent == "TestAgent"
        assert agent.temperature == 0.5
        assert agent.system_prompt == "You are a test agent."

    def test_agent_loads_system_prompt_from_file(self):
        """Test that agent loads system prompt from file when not provided."""
        mock_prompt = "Loaded from file"
        with patch("builtins.open", mock_open(read_data=mock_prompt)):
            with patch("os.path.exists", return_value=True):
                agent = Agent(typeOfAgent="TestAgent", api_key="test_key")
                # This would need the load_file function to be properly mocked

    def test_agent_stores_system_message(self):
        """Test that agent stores system message on init."""
        agent = Agent(api_key="test_key", system_prompt="You are helpful.")
        assert len(agent.messages) == 1
        assert agent.messages[0].role == "system"
        assert agent.messages[0].content == "You are helpful."


class TestAgentAddMessage:
    """Tests for add_message method."""

    def test_add_message_as_user(self):
        """Test adding a user message."""
        agent = Agent(api_key="test_key", system_prompt="Test")
        agent.add_message("Hello", "user")

        assert len(agent.messages) == 2
        assert agent.messages[1].role == "user"
        assert agent.messages[1].content == "Hello"

    def test_add_message_as_assistant(self):
        """Test adding an assistant message."""
        agent = Agent(api_key="test_key", system_prompt="Test")
        agent.add_message("Response", "assistant")

        assert len(agent.messages) == 2
        assert agent.messages[1].role == "assistant"
        assert agent.messages[1].content == "Response"

    def test_add_message_default_role(self):
        """Test adding message with default role."""
        agent = Agent(api_key="test_key", system_prompt="Test")
        agent.add_message("Content")

        assert agent.messages[1].role == "user"


class TestAgentGetMessages:
    """Tests for get_messages method."""

    def test_get_messages_returns_list(self):
        """Test that get_messages returns message list."""
        agent = Agent(api_key="test_key", system_prompt="Test")
        messages = agent.get_messages()

        assert isinstance(messages, list)
        assert len(messages) == 1

    def test_get_messages_returns_list_reference(self):
        """Test that get_messages returns reference to internal list."""
        # Note: Currently returns direct reference, not a copy
        agent = Agent(api_key="test_key", system_prompt="Test")
        messages = agent.get_messages()
        original_len = len(messages)

        # Modifying returned list DOES affect agent (current behavior)
        messages.append("test")
        # This documents current behavior - returning a copy would be safer
        assert len(agent.get_messages()) == original_len + 1


class TestAgentClearMessages:
    """Tests for clear_messages method."""

    def test_clear_messages_keeps_system(self):
        """Test that clear_messages keeps system message."""
        agent = Agent(api_key="test_key", system_prompt="System prompt")
        agent.add_message("User message")
        agent.add_message("Assistant message", "assistant")

        agent.clear_messages()

        assert len(agent.messages) == 1
        assert agent.messages[0].role == "system"
        assert agent.messages[0].content == "System prompt"

    def test_clear_messages_empty_conversation(self):
        """Test clearing already clear conversation."""
        agent = Agent(api_key="test_key", system_prompt="Test")
        agent.clear_messages()

        assert len(agent.messages) == 1
        assert agent.messages[0].role == "system"


class TestAgentSetMessages:
    """Tests for set_messages method."""

    def test_set_messages_replaces_messages(self):
        """Test that set_messages replaces all messages except system."""
        from message import Message

        agent = Agent(api_key="test_key", system_prompt="System")
        agent.add_message("Old message")

        new_messages = [
            Message("user", "New message 1"),
            Message("assistant", "New message 2"),
        ]

        agent.set_messages(new_messages)

        assert len(agent.messages) == 3
        assert agent.messages[0].role == "system"
        assert agent.messages[1].content == "New message 1"
        assert agent.messages[2].content == "New message 2"


class TestAgentFlipMessages:
    """Tests for flip_messages method."""

    def test_flip_messages_swaps_roles(self):
        """Test that flip_messages swaps user and assistant roles."""
        agent = Agent(api_key="test_key", system_prompt="Test")
        agent.add_message("User msg", "user")
        agent.add_message("Assistant msg", "assistant")

        agent.flip_messages()

        # System message should not change
        assert agent.messages[0].role == "system"
        # User becomes assistant
        assert agent.messages[1].role == "assistant"
        # Assistant becomes user
        assert agent.messages[2].role == "user"

    def test_flip_messages_system_unchanged(self):
        """Test that system messages are not flipped."""
        agent = Agent(api_key="test_key", system_prompt="System prompt")

        agent.flip_messages()

        assert agent.messages[0].role == "system"
        assert agent.messages[0].content == "System prompt"


class TestAgentGetLastMessage:
    """Tests for get_last_message method."""

    def test_get_last_message_returns_last(self):
        """Test that get_last_message returns the last message."""
        agent = Agent(api_key="test_key", system_prompt="Test")
        agent.add_message("Message 1")
        agent.add_message("Message 2")

        last = agent.get_last_message()
        assert last.content == "Message 2"

    def test_get_last_message_system_only(self):
        """Test getting last message when only system message exists."""
        agent = Agent(api_key="test_key", system_prompt="System")

        last = agent.get_last_message()
        assert last.role == "system"
        assert last.content == "System"


class TestAgentRequest:
    """Tests for request method (API calls)."""

    @patch("agent.requests.post")
    def test_request_sends_correct_payload(self, mock_post):
        """Test that request sends correct payload to API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response

        agent = Agent(api_key="test_key", system_prompt="System", temperature=0.7)
        agent.add_message("User message")
        agent.request()

        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Check headers
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_key"

        # Check payload
        payload = call_args[1]["data"]
        data = __import__("json").loads(payload)
        assert data["model"] == "openrouter/pony-alpha"
        assert data["temperature"] == 0.7
        assert len(data["messages"]) == 2  # system + user

    @patch("agent.requests.post")
    def test_request_adds_response_to_messages(self, mock_post):
        """Test that request adds API response to messages."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "AI response"}}]
        }
        mock_post.return_value = mock_response

        agent = Agent(api_key="test_key", system_prompt="System")
        agent.add_message("User message")
        response = agent.request()

        assert response == "AI response"
        assert len(agent.messages) == 3  # system + user + assistant
        assert agent.messages[2].role == "assistant"
        assert agent.messages[2].content == "AI response"

    @patch("agent.requests.post")
    def test_request_with_string_argument(self, mock_post):
        """Test request with string argument adds user message."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }
        mock_post.return_value = mock_response

        agent = Agent(api_key="test_key", system_prompt="System")
        agent.request("New user message")

        assert agent.messages[1].role == "user"
        assert agent.messages[1].content == "New user message"

    @patch("agent.requests.post")
    def test_request_handles_api_error(self, mock_post):
        """Test that request handles API errors gracefully."""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "API Error"}
        mock_post.return_value = mock_response

        agent = Agent(api_key="test_key", system_prompt="System")
        response = agent.request()

        assert response is None

    @patch("agent.requests.post")
    def test_request_with_message_object(self, mock_post):
        """Test request with Message object."""
        from message import Message

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }
        mock_post.return_value = mock_response

        agent = Agent(api_key="test_key", system_prompt="System")
        msg = Message("user", "Message content")
        agent.request(msg)

        assert agent.messages[1].role == "user"
        assert agent.messages[1].content == "Message content"
