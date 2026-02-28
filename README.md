# TalkingLLMs

A Python application that facilitates conversations between multiple LLM agents using the OpenRouter API. Create dynamic discussions between different AI agents with customizable system prompts and models.

## Features

- Multi-agent conversations with customizable personalities
- Support for multiple LLM models via OpenRouter
- PDF export of conversations
- Flexible agent configuration via system prompts
- Interactive CLI with guided setup

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd TalkingLLMs

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (if needed for PDF generation)
playwright install
```

## Configuration

Set your OpenRouter API key as an environment variable:

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

Or use a `.env` file with `python-dotenv`.

## Usage

### Interactive Mode

Run without arguments for interactive setup:

```bash
python main.py
```

You'll be prompted to enter:
- Agent names
- Model selection
- System prompts (or load from `prompts/systemPrompt{name}.txt`)
- Initial message
- Number of messages to generate

### Command Line Mode

Use flags for non-interactive execution:

```bash
python main.py \
  --name1 Alice \
  --name2 Bob \
  --system1 "You are a helpful coding assistant" \
  --system2 "You are a critical code reviewer" \
  --init "Review this function: def add(a, b): return a + b" \
  --messages 5 \
  --model google/gemini-2.0-flash-001 \
  --output conversation.pdf
```

### Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--name1` | `-n1` | First agent name | (interactive) |
| `--name2` | `-n2` | Second agent name | (interactive) |
| `--system1` | `-s1` | System prompt for first agent | (interactive) |
| `--system2` | `-s2` | System prompt for second agent | (interactive) |
| `--init` | `-i` | Initial message | (interactive) |
| `--messages` | `-m` | Number of messages | 5 |
| `--model` | `-M` | Model for both agents | google/gemini-2.0-flash-001 |
| `--model1` | `-m1` | Model for first agent | (uses --model) |
| `--model2` | `-m2` | Model for second agent | (uses --model) |
| `--output` | `-o` | Output PDF file | conversation.pdf |

### Available Models

- `google/gemini-2.0-flash-001`
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4o`
- `meta-llama/llama-3.3-70b-instruct`
- `deepseek/deepseek-chat`

## Project Structure

```
TalkingLLMs/
├── main.py                 # Entry point
├── talkingllms/
│   ├── __init__.py
│   ├── agent.py           # Agent class
│   ├── conversation.py    # Conversation handler
│   ├── message.py         # Message class
│   ├── pdf_generator.py   # PDF export
│   └── utils.py           # Utilities
├── tests/                 # Test suite
├── prompts/               # Agent system prompts
└── requirements.txt       # Dependencies
```

## Testing

```bash
# Run all tests
python -m unittest discover -s tests -v

# Run specific test file
python -m unittest tests.test_agent -v
```

## Requirements

- Python 3.10+
- requests
- playwright

## License

MIT