"""Tests for ConversationBtwAgents class."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from conversation import ConversationBtwAgents
from logger import ConversationLogger


class TestConversationInit:
    """Tests for ConversationBtwAgents initialization."""

    def test_conversation_stores_agents(self):
        """Test that conversation stores both agents."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(agent1, agent2)

        assert conv.agent1 == agent1
        assert conv.agent2 == agent2
        assert conv.name1 == "Alice"
        assert conv.name2 == "Bob"

    def test_conversation_default_first_agent(self):
        """Test that first agent is default when not specified."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(agent1, agent2)

        assert conv.current_agent == "Alice"

    def test_conversation_custom_first_agent(self):
        """Test setting custom first agent."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Bob")

        assert conv.current_agent == "Bob"

    def test_conversation_with_initial_message_first_agent(self):
        """Test conversation with initial message from first agent."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent1.request.return_value = "Hello from Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(
            agent1, agent2, initial_message="Start", first_agent="Alice"
        )

        agent1.request.assert_called_once_with("Start")
        agent2.add_message.assert_called_once_with("Hello from Alice")
        assert conv.current_agent == "Bob"  # Should switch to other agent

    def test_conversation_with_initial_message_second_agent(self):
        """Test conversation with initial message from second agent."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"
        agent2.request.return_value = "Hello from Bob"

        conv = ConversationBtwAgents(
            agent1, agent2, initial_message="Start", first_agent="Bob"
        )

        agent2.request.assert_called_once_with("Start")
        agent1.add_message.assert_called_once_with("Hello from Bob")
        assert conv.current_agent == "Alice"  # Should switch to other agent

    def test_conversation_with_logger(self, tmp_path):
        """Test conversation accepts logger."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        logger = ConversationLogger("Alice", "Bob", str(tmp_path / "logs"))

        conv = ConversationBtwAgents(agent1, agent2, logger=logger)

        assert conv.logger == logger


class TestConversationNextRequest:
    """Tests for next_request method."""

    def test_next_request_from_first_agent(self):
        """Test next request from first agent."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent1.request.return_value = "Response from Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Alice")
        response = conv.next_request()

        assert response == "Response from Alice"
        agent1.request.assert_called_once()
        agent2.add_message.assert_called_once_with("Response from Alice")

    def test_next_request_from_second_agent(self):
        """Test next request from second agent."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"
        agent2.request.return_value = "Response from Bob"

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Bob")
        response = conv.next_request()

        assert response == "Response from Bob"
        agent2.request.assert_called_once()
        agent1.add_message.assert_called_once_with("Response from Bob")

    def test_next_request_switches_agents(self):
        """Test that next_request switches current agent."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent1.request.return_value = "Response"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Alice")
        assert conv.current_agent == "Alice"

        conv.next_request()
        assert conv.current_agent == "Bob"

        conv.next_request()
        assert conv.current_agent == "Alice"

    def test_next_request_logs_message(self, tmp_path):
        """Test that next_request logs message when logger is present."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent1.request.return_value = "Response from Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        logger = Mock()

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Alice", logger=logger)
        conv.next_request()

        logger.log_message.assert_called_once_with(
            "Alice", "Response from Alice", "assistant"
        )

    def test_next_request_no_log_when_no_logger(self):
        """Test that next_request doesn't fail without logger."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent1.request.return_value = "Response"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Alice")
        # Should not raise
        response = conv.next_request()

        assert response == "Response"

    def test_next_request_handles_none_response(self, tmp_path):
        """Test that next_request handles None response."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent1.request.return_value = None
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        logger = ConversationLogger("Alice", "Bob", str(tmp_path / "logs"))

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Alice", logger=logger)
        response = conv.next_request()

        assert response is None
        agent2.add_message.assert_called_once_with(None)


class TestConversationGetCurrentAgent:
    """Tests for get_current_agent method."""

    def test_get_current_agent_returns_string(self):
        """Test that get_current_agent returns agent name."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Alice")

        assert conv.get_current_agent() == "Alice"

    def test_get_current_agent_updates_after_next_request(self):
        """Test that get_current_agent reflects agent switches."""
        agent1 = Mock()
        agent1.typeOfAgent = "Alice"
        agent1.request.return_value = "Response"
        agent2 = Mock()
        agent2.typeOfAgent = "Bob"

        conv = ConversationBtwAgents(agent1, agent2, first_agent="Alice")
        assert conv.get_current_agent() == "Alice"

        conv.next_request()
        assert conv.get_current_agent() == "Bob"
