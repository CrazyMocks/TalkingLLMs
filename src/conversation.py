import requests
import json
from typing import Optional
from agent import Agent
from logger import ConversationLogger


class ConversationBtwAgents:
    def __init__(
        self,
        agent1: Agent,
        agent2: Agent,
        initial_message: str = "",
        first_agent: Optional[str] = None,
        logger: Optional[ConversationLogger] = None,
    ):
        self.agent1 = agent1
        self.agent2 = agent2
        self.name1 = agent1.typeOfAgent
        self.name2 = agent2.typeOfAgent
        self.current_agent = first_agent if first_agent else self.name1
        self.logger = logger

        if initial_message:
            if self.current_agent == self.name1:
                response = self.agent1.request(initial_message)
                self.agent2.add_message(response)
            else:
                response = self.agent2.request(initial_message)
                self.agent1.add_message(response)
            self.current_agent = (
                self.name2 if self.current_agent == self.name1 else self.name1
            )

    def next_request(self) -> Optional[str]:
        if self.current_agent == self.name1:
            response = self.agent1.request()
            if response and self.logger:
                self.logger.log_message(self.name1, response, "assistant")
            self.agent2.add_message(response)
        else:
            response = self.agent2.request()
            if response and self.logger:
                self.logger.log_message(self.name2, response, "assistant")
            self.agent1.add_message(response)
        self.current_agent = (
            self.name2 if self.current_agent == self.name1 else self.name1
        )
        return response

    def get_current_agent(self) -> str:
        return self.current_agent
