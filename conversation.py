import requests
import json
from agent import Agent
class ConversationBtwAgents:
    def __init__(self, agent1, agent2, initial_message="", first_agent="Canvas"):
        self.canvas = agent1 if agent1.typeOfAgent == "Canvas" else agent2
        self.sentinel = agent2 if agent2.typeOfAgent == "Sentinel" else agent1
        self.current_agent = first_agent
        if initial_message:
            if self.current_agent == "Canvas":
                response = self.canvas.request(initial_message)
                self.sentinel.add_message(response)
            else:
                response = self.sentinel.request(initial_message)
                self.canvas.add_message(response)
            self.current_agent = "Canvas" if self.current_agent == "Sentinel" else "Sentinel"
    def next_request(self):
        if self.current_agent == "Canvas":
            response = self.canvas.request()
            self.sentinel.add_message(response)
        else:
            response = self.sentinel.request()
            self.canvas.add_message(response)
        self.current_agent = "Canvas" if self.current_agent == "Sentinel" else "Sentinel"
        return response
    def get_current_agent(self):
        return self.current_agent