import requests
import json
from message import Message
from utils import load_file
class Agent:
    def __init__(self, model="openrouter/pony-alpha", typeOfAgent='', api_key="",temperature=1, system_prompt=""):
        self.typeOfAgent = typeOfAgent
        self.system_prompt = system_prompt if system_prompt else load_file(f"prompts/defaultPrompt{typeOfAgent}")
        self.temperature = temperature
        self.messages = [Message("system", self.system_prompt)]
        self.model = model
        self.api_key = api_key
    def add_message(self, content, role="user"):
        self.messages.append(Message(role, content))
    def get_messages(self):
        return self.messages
    def clear_messages(self):
        self.messages = [Message("system", self.system_prompt)]
    def set_messages(self, messages):
        self.messages = [Message("system", self.system_prompt)] + messages
    def flip_messages(self):
        for message in self.messages:
            message.flip_role()
    def get_last_message(self):
        return self.messages[-1]
    def request(self, *args):
        if len(args) == 1:
            if type(args[0]) == Message:
                self.add_message(args[0].get_content(), args[0].get_role())
            else:
                self.add_message(args[0], "user")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            data=json.dumps({
                "model": self.model, 
                "messages": [message.to_dict() for message in self.messages],
                "temperature": self.temperature
            })
        )
        try:
            content = response.json()['choices'][0]['message']['content']
            self.add_message(content, "assistant")
            return content
        except KeyError as err:
            print (f"response:\n {response.json()}")
            return None
