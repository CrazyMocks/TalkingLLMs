import json
import os
from datetime import datetime
from pathlib import Path


class ConversationLogger:
    """Logger for real-time conversation backup."""

    def __init__(self, name1: str, name2: str, log_dir: str = "logs"):
        """Initialize logger with agent names and log directory.

        Args:
            name1: Name of first agent
            name2: Name of second agent
            log_dir: Directory for log files (default: logs)
        """
        self.name1 = name1
        self.name2 = name2
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"conversation_{name1}_{name2}_{timestamp}.jsonl"
        self.metadata_file = (
            self.log_dir / f"conversation_{name1}_{name2}_{timestamp}_metadata.json"
        )

        self._write_metadata()

    def _write_metadata(self) -> None:
        """Write initial metadata to separate file."""
        metadata = {
            "agent1": self.name1,
            "agent2": self.name2,
            "started_at": datetime.now().isoformat(),
            "log_file": str(self.log_file.name),
        }
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def log_message(self, sender: str, content: str, role: str = "assistant") -> None:
        """Log a single message to the JSONL file.

        Args:
            sender: Name of the agent sending the message
            content: Message content
            role: Message role (user/assistant/system)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "role": role,
            "content": content,
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()

    def get_log_path(self) -> str:
        """Return the path to the log file."""
        return str(self.log_file)
