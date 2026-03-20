"""Agent module for managing LLM conversations."""

import json

import requests

from message import Message
from utils import load_file


class Agent:
    """Represents an LLM agent with conversation capabilities."""

    def __init__(
        self,
        model="openrouter/pony-alpha",
        type_of_agent="",
        api_key="",
        temperature=1,
        system_prompt="",
    ):
        """Initialize the agent.

        Args:
            model: The LLM model to use.
            type_of_agent: Type identifier for the agent.
            api_key: API key for the LLM service.
            temperature: Sampling temperature for generation.
            system_prompt: System prompt for the agent.
        """
        self.type_of_agent = type_of_agent
        self.system_prompt = (
            system_prompt
            if system_prompt
            else load_file(f"prompts/defaultPrompt{type_of_agent}")
        )
        self.temperature = temperature
        self.messages = [Message("system", self.system_prompt)]
        self.model = model
        self.api_key = api_key

    def add_message(self, content, role="user"):
        """Add a message to the conversation.

        Args:
            content: The message content.
            role: The role of the message (user/assistant/system).
        """
        self.messages.append(Message(role, content))

    def get_messages(self):
        """Get all messages in the conversation.

        Returns:
            List of Message objects.
        """
        return self.messages

    def clear_messages(self):
        """Clear all messages except the system prompt."""
        self.messages = [Message("system", self.system_prompt)]

    def set_messages(self, messages):
        """Set messages, keeping system prompt first.

        Args:
            messages: List of Message objects to set.
        """
        self.messages = [Message("system", self.system_prompt)] + messages

    def flip_messages(self):
        """Flip roles of all messages in the conversation."""
        for message in self.messages:
            message.flip_role()

    def get_last_message(self):
        """Get the last message in the conversation.

        Returns:
            The last Message object.
        """
        return self.messages[-1]

    def request(self, *args):
        """Send a request to the LLM API.

        Args:
            *args: Optional message content or Message object.

        Returns:
            The response content from the LLM, or None on error.
        """
        if len(args) == 1:
            if isinstance(args[0], Message):
                self.add_message(args[0].get_content(), args[0].get_role())
            else:
                self.add_message(args[0], "user")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            data=json.dumps(
                {
                    "model": self.model,
                    "messages": [message.to_dict() for message in self.messages],
                    "temperature": self.temperature,
                }
            ),
        )
        try:
            content = response.json()["choices"][0]["message"]["content"]
            self.add_message(content, "assistant")
            return content
        except KeyError:
            print(f"response:\n {response.json()}")
            return None
