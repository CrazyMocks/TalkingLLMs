"""TalkingLLMs - Generate conversations between LLM agents."""

__version__ = "0.1.0"

from talkingllms.agent import Agent
from talkingllms.conversation import ConversationBtwAgents
from talkingllms.message import Message

__all__ = ["Agent", "ConversationBtwAgents", "Message"]
