# TalkingLLMs

A Python application that enables conversations between multiple LLM agents using the OpenRouter API. Create dynamic discussions between different AI models with customizable personalities and system prompts.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## What Does It Do?

TalkingLLMs allows you to set up a conversation between two AI agents. Each agent can have:
- A unique name (e.g., "Alice", "Bob", "SkepticalReviewer")
- A custom system prompt defining their personality
- A different LLM model

The agents take turns responding to each other, and the entire conversation is exported as a PDF.

**Example use cases:**
- Generate a debate between two AI perspectives
- Create a coding interview with interviewer/interviewee agents
- Simulate a customer support conversation
- Produce educational dialogues between teacher/student agents

## Features

- 🤖 Multi-agent conversations with customizable personalities
- 📄 PDF export of complete conversations
- 🔧 Multiple ways to run: interactive, command-line, or config file
- 🌐 Access to 20+ popular LLM models via OpenRouter
- 💬 Both agents can use different models

## Prerequisites

Before you begin, you need:

1. **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
2. **OpenRouter API Key** - [Get a free key](https://openrouter.ai/)

   > OpenRouter provides free credits for new users. You don't need to pay to try this!

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/TalkingLLMs.git
cd TalkingLLMs

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for PDF generation)
playwright install chromium
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_actual_api_key_here
```

> Get your free API key at: https://openrouter.ai/settings/keys

### 3. Run the Application

**Option A: Interactive Mode (Recommended for Beginners)**

```bash
python src/main.py
```

The program will guide you through:
- Choosing agent names
- Selecting models (or pressing Enter for defaults)
- Writing system prompts
- Setting the initial message
- Choosing how many messages to generate

**Option B: Config File (Best for Reusability)**

Create a config file (see `config.example` for reference):

```bash
python src/main.py --config config.example
```

**Option C: Command Line Arguments**

```bash
python src/main.py \
  --name1 Alice \
  --name2 Bob \
  --system1 "You are a friendly AI assistant who loves technology." \
  --system2 "You are a skeptical reviewer who questions everything." \
  --init "What do you think about artificial intelligence?" \
  --messages 5
```

## Config File Format

Create a `.cfg` file with human-readable settings:

```ini
# My conversation config
# Comments start with #

# Agent names
name1: Alice
name2: Bob

# Models to use (model IDs from OpenRouter)
model1: google/gemini-2.0-flash-001
model2: google/gemini-2.0-flash-001

# Use free models (true/false)
paid: false

# Number of messages to exchange
messages: 5

# System prompts (what defines each agent's personality)
system1: You are a helpful coding assistant who loves explaining concepts.
system2: You are a critical code reviewer who focuses on bugs and edge cases.

# Initial message that starts the conversation
init: Can you explain how Python's list comprehension works?
```

Run it with:
```bash
python src/main.py --config my_config.cfg
```

You can also load system prompts from files:

```ini
# Load prompts from files instead of inline
system1_file: prompts/my_custom_prompt.txt
system2_file: prompts/another_prompt.txt
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--name1` | `-n1` | First agent name | (prompted) |
| `--name2` | `-n2` | Second agent name | (prompted) |
| `--system1` | `-s1` | System prompt for first agent | (prompted) |
| `--system2` | `-s2` | System prompt for second agent | (prompted) |
| `--init` | `-i` | Initial message | (prompted) |
| `--messages` | `-m` | Number of messages | 3 |
| `--model` | `-M` | Model for both agents | google/gemini-2.0-flash-001 |
| `--model1` | `-m1` | Model for first agent | (uses --model) |
| `--model2` | `-m2` | Model for second agent | (uses --model) |
| `--output` | `-o` | Output PDF filename | conversation.pdf |
| `--config` | `-c` | Path to config file | (none) |

## Available Models

When running in interactive mode, you'll see a list of 20 popular models. Some recommended free models:

- `google/gemini-2.0-flash-001` (default, free)
- `meta-llama/llama-3.3-70b-instruct`
- `qwen/qwen3-coder`
- `google/gemma-3-27b-it`

For full list, run the app in interactive mode.

## Output

The conversation is saved as a PDF file (default: `conversation.pdf`) containing:
- Agent names
- Models used
- Full message history
- Timestamps

## Project Structure

```
TalkingLLMs/
├── src/
│   ├── main.py              # Main entry point
│   ├── agent.py             # Agent implementation
│   ├── conversation.py     # Conversation logic
│   ├── message.py          # Message handling
│   ├── pdf_generator.py    # PDF export
│   └── utils.py            # Helper functions
├── default/
│   └── initialMessage      # Default starting message
├── config.example          # Example config file
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md
```

## Troubleshooting

### "OPENROUTER_API_KEY environment variable not set"

Make sure your `.env` file contains the correct API key:
```
OPENROUTER_API_KEY=sk-or-...
```

### PDF generation fails

Ensure Playwright browsers are installed:
```bash
playwright install chromium
```

### Import errors

Make sure you've activated the virtual environment:
```bash
source venv/bin/activate  # Linux/macOS
```

## Requirements

- Python 3.10+
- requests >= 2.28.0
- playwright >= 1.40.0

## License

MIT License - Feel free to use and modify!

---

Made with 🤖 for AI enthusiasts
