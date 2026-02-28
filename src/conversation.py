import requests
import json
from agent import Agent


class ConversationBtwAgents:
    def __init__(self, agent1, agent2, initial_message="", first_agent=None):
        self.agent1 = agent1
        self.agent2 = agent2
        self.name1 = agent1.typeOfAgent
        self.name2 = agent2.typeOfAgent
        self.current_agent = first_agent if first_agent else self.name1
        if initial_message:
            if self.current_agent == self.name1:
                response = self.agent1.request(initial_message)
                self.agent2.add_message(response)
            else:
                response = self.agent2.request(initial_message)
                self.agent1.add_message(response)
            self.current_agent = self.name2 if self.current_agent == self.name1 else self.name1

    def next_request(self):
        if self.current_agent == self.name1:
            response = self.agent1.request()
            self.agent2.add_message(response)
        else:
            response = self.agent2.request()
            self.agent1.add_message(response)
        self.current_agent = self.name2 if self.current_agent == self.name1 else self.name1
        return response

    def get_current_agent(self):
        return self.current_agent
