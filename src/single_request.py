"""Single request module for one-off LLM requests."""

import json

import requests


class SingleRequest:
    """Represents a single request to an LLM."""

    def __init__(
        self,
        initial_message="",
        model="openrouter/pony-alpha",
        system_prompt="",
        api_key="",
        temperature=1,
    ):
        """Initialize a single request.

        Args:
            initial_message: Optional initial message to add.
            model: The LLM model to use.
            system_prompt: System prompt for the request.
            api_key: API key for the LLM service.
            temperature: Sampling temperature for generation.
        """
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.messages = []
        if initial_message:
            self.add_message(initial_message)
        self.model = model
        self.api_key = api_key

    def add_message(self, content):
        """Add a message to the conversation.

        Args:
            content: The message content.
        """
        self.messages.append(content)

    def get_messages(self):
        """Get all messages.

        Returns:
            List of messages.
        """
        return self.messages

    def clear(self):
        """Clear all messages."""
        self.messages = []

    def get_last_message(self):
        """Get the last message.

        Returns:
            The last message content.
        """
        return self.messages[-1]

    def next_message(self):
        """Send request to LLM and get next message.

        Returns:
            The response content, or None on error.
        """
        model = self.model
        system_prompt = self.system_prompt

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        for message in self.messages:
            messages.append({"role": "user", "content": message})

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            data=json.dumps(
                {
                    "model": model,
                    "messages": messages,
                    "temperature": self.temperature,
                }
            ),
        )
        try:
            content = response.json()["choices"][0]["message"]["content"]
            self.add_message(content)
            return content
        except KeyError:
            print(f"response:\n {response.json()}")
            return None
