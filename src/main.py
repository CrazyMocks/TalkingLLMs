import argparse
import os
import sys
from datetime import datetime

from agent import Agent
from conversation import ConversationBtwAgents
from message import Message
from utils import load_file
from openrouterModels import fetch_20_most_popular_openrouter_models

defaultModel = 'arcee-ai/trinity-large-preview:free'
def get_api_key() -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        print("Please set it with: export OPENROUTER_API_KEY=your_key")
        sys.exit(1)
    return api_key


def get_available_models():
    return fetch_20_most_popular_openrouter_models()


def prompt_model_selection(prompt: str, default: str = "") -> str:
    value = input(prompt).strip()
    return value if value else default


def generate_conversation(
    name1: str,
    name2: str,
    system_prompt1: str,
    system_prompt2: str,
    initial_message: str,
    num_messages: int,
    model1: str,
    model2: str,
    api_key: str,
) -> list[tuple[Message, str]]:
    agent1 = Agent(
        model=model1,
        typeOfAgent=name1,
        api_key=api_key,
        system_prompt=system_prompt1,
    )
    agent2 = Agent(
        model=model2,
        typeOfAgent=name2,
        api_key=api_key,
        system_prompt=system_prompt2,
    )

    conv = ConversationBtwAgents(
        agent1,
        agent2,
        initial_message=initial_message,
        first_agent=name1,
    )

    messages = []
    messages.append((Message("user", initial_message), name1))

    current_agent = name2
    for _ in range(num_messages):
        response = conv.next_request()
        if response is None:
            print(f"Warning: Failed to get response from {current_agent}, stopping conversation")
            break
        messages.append((Message("assistant", response), current_agent))
        current_agent = name1 if current_agent == name2 else name2

    return messages


def main():
    parser = argparse.ArgumentParser(
        description="Generate conversation between two LLM agents"
    )
    parser.add_argument(
        "--name1", "-n1", help="Name of first agent", default="Alice"
    )
    parser.add_argument(
        "--name2", "-n2", help="Name of second agent", default="Bob"
    )
    parser.add_argument(
        "--system1", "-s1", help="System prompt for first agent", default=""
    )
    parser.add_argument(
        "--system2", "-s2", help="System prompt for second agent", default=""
    )
    parser.add_argument(
        "--init", "-i", help="Initial message", default="Hej, porozmawiajmy o czymś interesującym"
    )
    parser.add_argument(
        "--messages", "-m", type=int, help="Number of messages to generate", default=3
    )
    parser.add_argument(
        "--model", "-M", help="Model to use for both agents", 
        default="google/gemini-2.0-flash-001"
    )
    parser.add_argument(
        "--model1", "-m1", help="Model for first agent", 
        default=None
    )
    parser.add_argument(
        "--model2", "-m2", help="Model for second agent", 
        default=None
    )
    parser.add_argument(
        "--output", "-o", help="Output PDF file", default="conversation.pdf"
    )

    args = parser.parse_args()

    api_key = get_api_key()

    print("\n=== LLM Conversation Generator ===\n")

    models = get_available_models()
    models_formated_names = list(models.keys())
    
    
    if args.name1 and args.name2 and args.system1 and args.system2 and args.init:
        name1 = args.name1
        name2 = args.name2
        system_prompt1 = args.system1
        system_prompt2 = args.system2
        initial_message = args.init
        model1 = args.model1 or args.model
        model2 = args.model2 or args.model
    else:
        while True:
            name1 = prompt_model_selection("First agent name (default Alice): ")
            if name1.strip():
                break
            else:
                name1 = "Alice"
                print(f"  Defaulting to {name1}")
                break
        
        while True:
            name2 = prompt_model_selection("Second agent name (default Bob): ")
            if name2.strip():
                break
            else:
                name2 = "Bob"
                print(f"  Defaulting to {name2}")
                break
        
        print("\nAvailable models:")
        for i, m in enumerate(models_formated_names, 1):
            print(f"  {i}. {m}")
        
        print(f"Model for {name1}:")
        model1_choice = prompt_model_selection(f"  (number or Enter for {defaultModel}): ")
        model1 = models[models_formated_names[0]]
        if model1_choice:
            try:
                idx = int(model1_choice) - 1
                if 0 <= idx < len(models):
                    model1 = models[models_formated_names[idx]]
            except ValueError:
                model1 = model1_choice
        
        print(f"\nModel for {name2}:")
        model2_choice = prompt_model_selection(f"  (number or Enter for same as above): ")
        model2 = model1
        if model2_choice:
            try:
                idx = int(model2_choice) - 1
                if 0 <= idx < len(models):
                    model2 = models[models_formated_names[idx]]
            except ValueError:
                model2 = model2_choice
        print(f"\nEnter system prompt for {name1} (press Enter for default):")
        system_prompt1 = prompt_model_selection(
            "  > ", 
            load_file(f"prompts/systemPrompt{name1}.txt") if os.path.exists(f"prompts/defaultPrompt{name1}.txt") else "You are a helpful assistant."
        )
        print(f"\nEnter system prompt for {name2} (press Enter for default):")
        system_prompt2 = prompt_model_selection(
            "  > ",
            load_file(f"prompts/systemPrompt{name2}.txt") if os.path.exists(f"prompts/defaultPrompt{name2}.txt") else "You are a helpful assistant."
        )
        while True:
            print("\nEnter initial message:")
            initial_message = prompt_model_selection("  > ")
            if initial_message.strip():
                break
            else:
                initial_message = load_file(f"prompts/initialMessage.txt") if os.path.exists(f"prompts/initialMessage.txt") else "Hello!"
                break


    num_messages = args.messages

    print(f"\n=== Generating {num_messages} messages between {name1} and {name2} ===\n")

    messages = generate_conversation(
        name1=name1,
        name2=name2,
        system_prompt1=system_prompt1,
        system_prompt2=system_prompt2,
        initial_message=initial_message,
        num_messages=num_messages,
        model1=model1,
        model2=model2,
        api_key=api_key,
    )

    from pdf_generator import generate_pdf
    generate_pdf(messages, args.output, name1, name2, model1, model2)
    
    print(f"\n=== Conversation saved to {args.output} ===")


if __name__ == "__main__":
    main()
