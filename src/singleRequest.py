import requests
import json


class SingleRequest:
    def __init__(
        self,
        initial_message="",
        model="openrouter/pony-alpha",
        system_prompt="",
        api_key="",
        temperature=1,
    ):
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.messages = []
        if initial_message:
            self.add_message(initial_message)
        self.model = model
        self.api_key = api_key

    def add_message(self, content):
        self.messages.append(content)

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []

    def get_last_message(self):
        return self.messages[-1]

    def next_message(self):
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
                {"model": model, "messages": messages, "temperature": self.temperature}
            ),
        )
        try:
            content = response.json()["choices"][0]["message"]["content"]
            self.add_message(content)
            return content
        except KeyError as err:
            print(f"response:\n {response.json()}")
            return None
