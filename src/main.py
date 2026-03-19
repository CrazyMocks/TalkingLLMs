import argparse
import os
import sys
from datetime import datetime
from typing import Optional

from agent import Agent
from conversation import ConversationBtwAgents
from logger import ConversationLogger
from message import Message
from utils import load_file
from openrouterModels import fetch_20_most_popular_openrouter_models

defaultModel = 'arcee-ai/trinity-large-preview:free'


def parse_config(config_path: str) -> dict:
    """Parse a human-readable config file.
    
    Format:
        # Comments start with #
        key: value
        model1: google/gemini-2.0-flash-001
        system1: You are a helpful assistant.
        system1_file: path/to/file.txt  # load from file
    """
    config = {}
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            config[key] = value
    
    resolved_config = {}
    for key, value in config.items():
        if key.endswith('_file'):
            base_key = key[:-5]
            try:
                resolved_config[base_key] = load_file(value)
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found for {key}: {value}")
        else:
            resolved_config[key] = value
    
    return resolved_config


def load_env():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(env_path)


def get_api_key() -> str:
    load_env()
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        print("Please set it in .env file or export OPENROUTER_API_KEY=your_key")
        sys.exit(1)
    return api_key


def get_available_models(paid=False):
    return fetch_20_most_popular_openrouter_models(paid)


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
    log_dir: str = "logs",
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

    logger = ConversationLogger(name1, name2, log_dir)
    logger.log_message(name1, initial_message, "user")
    print(f"Real-time logging enabled: {logger.get_log_path()}")

    conv = ConversationBtwAgents(
        agent1,
        agent2,
        initial_message=initial_message,
        first_agent=name1,
        logger=logger,
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
        print(messages[-1][0].get_content())
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
        "--systemPath1", "-sp1", help="System prompt file path for first agent", default=""
    )
    parser.add_argument(
        "--systemPath2", "-sp2", help="System prompt file path for second agent", default=""
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
    parser.add_argument(
        "--config", "-c", help="Path to config file (human-readable format)", 
        default=None
    )

    args = parser.parse_args()

    config_values = {}
    if args.config:
        config_values = parse_config(args.config)
        print(f"Loaded config from: {args.config}")

    api_key = get_api_key()

    print("\n=== LLM Conversation Generator ===\n")
    
    config_paid = config_values.get('paid', '').lower()
    if config_paid in ['true', '1', 'yes', 'y']:
        paidFlag = True
    elif config_paid in ['false', '0', 'no', 'n', '']:
        paidFlag = False
    else:
        paid = ''
        while paid not in ['y', 'n', 'Y', 'N']:
            paid = input("Do you want use paid models? (y/n): ")
        paidFlag = paid in ['y', 'Y']
    
    config_model1 = config_values.get('model1', '')
    config_model2 = config_values.get('model2', '')
    has_config_models = bool(config_model1 and config_model2)
    
    if has_config_models:
        print(f"Using models from config: {config_model1}, {config_model2}")
    else:
        models = get_available_models(paidFlag)
        models_formated_names = list(models.keys())
    
    
    config_name1 = config_values.get('name1', '')
    config_name2 = config_values.get('name2', '')
    config_system1 = config_values.get('system1', '')
    config_system2 = config_values.get('system2', '')
    config_init = config_values.get('init', '')
    config_messages = config_values.get('messages', '')

    has_cli_args = args.name1 and args.name2 and args.system1 and args.system2 and args.init
    has_config_args = config_name1 and config_name2 and config_system1 and config_system2 and config_init

    if has_cli_args:
        name1 = args.name1
        name2 = args.name2
        system_prompt1 = args.system1
        system_prompt2 = args.system2
        initial_message = args.init
        model1 = args.model1 or args.model
        model2 = args.model2 or args.model
        num_messages = args.messages
    elif has_config_args:
        name1 = config_name1
        name2 = config_name2
        system_prompt1 = config_system1
        system_prompt2 = config_system2
        initial_message = config_init
        model1 = config_model1
        model2 = config_model2
        num_messages = int(config_messages) if config_messages else args.messages
    else:
        default_name1 = config_name1 or 'Alice'
        default_name2 = config_name2 or 'Bob'
        
        while True:
            prompt_text = f"First agent name (default {default_name1}): "
            name1 = prompt_model_selection(prompt_text)
            if name1.strip():
                break
            else:
                name1 = default_name1
                print(f"  Defaulting to {name1}")
                break
        
        while True:
            prompt_text = f"Second agent name (default {default_name2}): "
            name2 = prompt_model_selection(prompt_text)
            if name2.strip():
                break
            else:
                name2 = default_name2
                print(f"  Defaulting to {name2}")
                break
        
        if not has_config_models:
            print("\nAvailable models:")
            for i, m in enumerate(models_formated_names, 1):
                print(f"  {i}. {m}")
            
            default_m1 = config_model1 if config_model1 else defaultModel
            print(f"Model for {name1}:")
            model1_choice = prompt_model_selection(f"  (number or Enter for {default_m1}): ")
            model1 = config_model1 or defaultModel
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
        else:
            model1 = config_model1
            model2 = config_model2
        
        default_sys1 = config_system1 or (load_file(f"prompts/systemPrompt{name1}.txt") if os.path.exists(f"prompts/defaultPrompt{name1}.txt") else "You are a helpful assistant.")
        print(f"\nEnter system prompt for {name1} (press Enter for default):")
        system_prompt1 = prompt_model_selection("  > ", default_sys1)
        
        default_sys2 = config_system2 or (load_file(f"prompts/systemPrompt{name2}.txt") if os.path.exists(f"prompts/defaultPrompt{name2}.txt") else "You are a helpful assistant.")
        print(f"\nEnter system prompt for {name2} (press Enter for default):")
        system_prompt2 = prompt_model_selection("  > ", default_sys2)
        
        default_init = config_init or (load_file(f"default/initialMessage") if os.path.exists(f"default/initialMessage") else "Hello!")
        while True:
            print("\nEnter initial message:")
            initial_message = prompt_model_selection("  > ", default_init)
            if initial_message.strip():
                break
            else:
                initial_message = default_init
                break
        
        default_msgs = config_messages or str(args.messages)
        while True:
            print(f"\nNumber of messages to generate (default {default_msgs}):")
            num_messages_input = prompt_model_selection("  > ")
            if num_messages_input.strip():
                try:
                    num_messages = int(num_messages_input)
                    break
                except ValueError:
                    print("  Please enter a valid number")
            else:
                num_messages = int(default_msgs)
                print(f"  Defaulting to {num_messages}")
                break

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
