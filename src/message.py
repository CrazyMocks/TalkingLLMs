"""Message module for conversation messages."""


class Message:
    """Represents a single message in a conversation."""

    def __init__(self, role, content):
        """Initialize a message.

        Args:
            role: The role of the message (user/assistant/system).
            content: The content of the message.
        """
        self.role = role
        self.content = content

    def to_dict(self):
        """Convert message to dictionary format.

        Returns:
            Dictionary with role and content keys.
        """
        return {"role": self.role, "content": self.content}

    def __str__(self):
        """Return string representation of message.

        Returns:
            String in format "role: content".
        """
        return f"{self.role}: {self.content}"

    def get_role(self):
        """Get the role of the message.

        Returns:
            The role string.
        """
        return self.role

    def get_content(self):
        """Get the content of the message.

        Returns:
            The content string.
        """
        return self.content

    def set_role(self, role):
        """Set the role of the message.

        Args:
            role: The new role (user/assistant/system).

        Raises:
            ValueError: If role is not valid.
        """
        if role not in ["user", "assistant", "system"]:
            raise ValueError("Invalid role. Must be one of: user, assistant, system")
        self.role = role

    def set_content(self, content):
        """Set the content of the message.

        Args:
            content: The new content.
        """
        self.content = content

    def is_user(self):
        """Check if message is from user.

        Returns:
            True if role is user.
        """
        return self.role == "user"

    def is_assistant(self):
        """Check if message is from assistant.

        Returns:
            True if role is assistant.
        """
        return self.role == "assistant"

    def is_system(self):
        """Check if message is a system message.

        Returns:
            True if role is system.
        """
        return self.role == "system"

    def flip_role(self):
        """Flip role between user and assistant."""
        if self.role == "user":
            self.role = "assistant"
        elif self.role == "assistant":
            self.role = "user"
