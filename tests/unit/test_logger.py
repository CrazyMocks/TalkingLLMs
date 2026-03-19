"""Tests for ConversationLogger class."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from logger import ConversationLogger


class TestLoggerCreation:
    """Tests for logger initialization."""

    def test_logger_creates_log_directory(self, tmp_path):
        """Test that logger creates log directory if it doesn't exist."""
        log_dir = tmp_path / "test_logs"
        ConversationLogger("Alice", "Bob", str(log_dir))
        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_logger_uses_existing_directory(self, tmp_path):
        """Test that logger works with existing directory."""
        log_dir = tmp_path / "existing_logs"
        log_dir.mkdir()
        ConversationLogger("Alice", "Bob", str(log_dir))
        assert log_dir.exists()

    def test_logger_creates_log_file_on_first_log(self, tmp_path):
        """Test that logger creates log file on first log message."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        # Log file doesn't exist until first message is logged
        assert not logger.log_file.exists()
        logger.log_message("Alice", "Hello")
        assert logger.log_file.exists()
        assert logger.log_file.suffix == ".jsonl"

    def test_logger_creates_metadata_file(self, tmp_path):
        """Test that logger creates metadata file."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        assert logger.metadata_file.exists()
        assert logger.metadata_file.suffix == ".json"

    def test_log_file_naming_includes_names(self, tmp_path):
        """Test that log file includes agent names."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        assert "Alice" in logger.log_file.name
        assert "Bob" in logger.log_file.name

    def test_log_file_naming_includes_timestamp(self, tmp_path):
        """Test that log file includes timestamp."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        # Should contain date pattern (YYYYMMDD_HHMMSS)
        assert "conversation_Alice_Bob_" in logger.log_file.name


class TestLoggerMetadata:
    """Tests for metadata file content."""

    def test_metadata_contains_agent_names(self, tmp_path):
        """Test that metadata contains agent names."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))

        with open(logger.metadata_file) as f:
            metadata = json.load(f)

        assert metadata["agent1"] == "Alice"
        assert metadata["agent2"] == "Bob"

    def test_metadata_contains_start_time(self, tmp_path):
        """Test that metadata contains start timestamp."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))

        with open(logger.metadata_file) as f:
            metadata = json.load(f)

        assert "started_at" in metadata
        assert isinstance(metadata["started_at"], str)

    def test_metadata_contains_log_file_reference(self, tmp_path):
        """Test that metadata references log file."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))

        with open(logger.metadata_file) as f:
            metadata = json.load(f)

        assert "log_file" in metadata
        assert metadata["log_file"] == logger.log_file.name


class TestLoggerLogMessage:
    """Tests for log_message method."""

    def test_log_single_message(self, tmp_path):
        """Test logging a single message."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        logger.log_message("Alice", "Hello", "user")

        with open(logger.log_file) as f:
            lines = f.readlines()

        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["sender"] == "Alice"
        assert data["content"] == "Hello"
        assert data["role"] == "user"

    def test_log_multiple_messages(self, tmp_path):
        """Test logging multiple messages."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))

        logger.log_message("Alice", "Hello", "user")
        logger.log_message("Bob", "Hi there!", "assistant")
        logger.log_message("Alice", "How are you?", "user")

        with open(logger.log_file) as f:
            lines = f.readlines()

        assert len(lines) == 3

        data1 = json.loads(lines[0])
        assert data1["sender"] == "Alice"
        assert data1["content"] == "Hello"

        data2 = json.loads(lines[1])
        assert data2["sender"] == "Bob"
        assert data2["content"] == "Hi there!"

    def test_log_message_contains_timestamp(self, tmp_path):
        """Test that logged message contains timestamp."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        logger.log_message("Alice", "Hello", "user")

        with open(logger.log_file) as f:
            lines = f.readlines()

        data = json.loads(lines[0])
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)
        # Should be ISO format
        assert "T" in data["timestamp"]

    def test_log_message_default_role(self, tmp_path):
        """Test that default role is assistant."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        logger.log_message("Alice", "Hello")  # No role specified

        with open(logger.log_file) as f:
            lines = f.readlines()

        data = json.loads(lines[0])
        assert data["role"] == "assistant"

    def test_log_message_unicode_content(self, tmp_path):
        """Test logging unicode content."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        logger.log_message("Alice", "Hello 世界 🌍", "user")

        with open(logger.log_file, encoding="utf-8") as f:
            lines = f.readlines()

        data = json.loads(lines[0])
        assert data["content"] == "Hello 世界 🌍"

    def test_log_message_empty_content(self, tmp_path):
        """Test logging empty content."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        logger.log_message("Alice", "", "assistant")

        with open(logger.log_file) as f:
            lines = f.readlines()

        data = json.loads(lines[0])
        assert data["content"] == ""

    def test_log_message_multiline_content(self, tmp_path):
        """Test logging multiline content."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        multiline = "Line 1\nLine 2\nLine 3"
        logger.log_message("Alice", multiline, "assistant")

        with open(logger.log_file) as f:
            lines = f.readlines()

        assert len(lines) == 1  # Should still be one line (JSONL format)
        data = json.loads(lines[0])
        assert data["content"] == multiline


class TestLoggerGetLogPath:
    """Tests for get_log_path method."""

    def test_get_log_path_returns_string(self, tmp_path):
        """Test that get_log_path returns path as string."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        path = logger.get_log_path()
        assert isinstance(path, str)
        assert path.endswith(".jsonl")

    def test_get_log_path_matches_log_file(self, tmp_path):
        """Test that get_log_path matches log_file attribute."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        assert logger.get_log_path() == str(logger.log_file)


class TestLoggerPersistence:
    """Tests for log file persistence."""

    def test_logged_data_persists(self, tmp_path):
        """Test that logged data persists in file."""
        log_dir = tmp_path / "logs"
        logger = ConversationLogger("Alice", "Bob", str(log_dir))
        logger.log_message("Alice", "Test message", "user")

        # Read back the data
        with open(logger.log_file) as f:
            lines = f.readlines()

        data = json.loads(lines[0])
        assert data["sender"] == "Alice"
        assert data["content"] == "Test message"
        assert data["role"] == "user"
