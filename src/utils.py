"""Utility functions for the TalkingLLMs application."""

import importlib
import inspect
import os
import re
import types

from message import Message


def clear_files():
    """Clear message files."""
    with open("messagesA", "w") as f:
        f.write("")
    with open("messagesB", "w") as f:
        f.write("")


def save_message_to_file(message, file, sep=""):
    """Save a message to a file with optional separator.

    Args:
        message: The message content to save.
        file: The file path to save to.
        sep: Optional separator to write after the message.
    """
    with open(file, "a") as f:
        f.write(message)
        if sep:
            f.write(f"\n{sep}\n")


def export_messages(messages, sep=""):
    """Export messages to files, alternating between agents.

    Args:
        messages: List of messages to export.
        sep: Optional separator between messages.
    """
    current_agent = "A"
    for message in messages:
        if current_agent == "A":
            save_message_to_file(message, "messagesA", sep)
        else:
            save_message_to_file(message, "messagesB", sep)
        current_agent = "B" if current_agent == "A" else "A"


def load_file(file):
    """Load contents of a file.

    Args:
        file: Path to the file.

    Returns:
        Contents of the file as string.
    """
    with open(file, "r", encoding="utf-8") as f:
        txt = f.read()
    return txt


def load_initial_message(initial_message_file, project_discription):
    """Load initial message with project description.

    Args:
        initial_message_file: Path to initial message template.
        project_discription: Path to project description or description text.

    Returns:
        Message object with populated template.
    """
    proj_desc = ""
    if os.path.exists(project_discription):
        proj_desc = load_file(project_discription)
    else:
        proj_desc = project_discription
    template = load_file(initial_message_file)
    return Message("user", template.replace("<Project Description>", proj_desc))


def refresh_chat(conv):
    """Refresh chat by clearing and re-exporting messages.

    Args:
        conv: Conversation object.
    """
    clear_files()
    export_messages(conv.get_messages())


def parse_and_save_files(response_text, output_dir="project_root"):
    """Parse file tags from response and save to disk.

    Args:
        response_text: Text containing <file path="..."> tags.
        output_dir: Directory to save files to.
    """
    # Regex szukający tagów <file path="...">...</file>
    # flaga re.DOTALL sprawia, że kropka łapie też znaki nowej linii
    pattern = r'<file path="(.*?)">(.*?)</file>'

    files = re.findall(pattern, response_text, re.DOTALL)

    if not files:
        print("Nie znaleziono plików w odpowiedzi modelu.")
        return

    for path, content in files:
        # Usuń ewentualne białe znaki z początku/końca treści (opcjonalne)
        content = content.strip()

        full_path = os.path.join(output_dir, path)
        dir_name = os.path.dirname(full_path)

        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"--> Utworzono: {full_path}")


def get_last_sentence(text):
    """Get last 5 sentences from text.

    Args:
        text: Input text.

    Returns:
        Last 5 sentences joined.
    """
    sentences = text.split(".")
    return "".join(sentences[-5:])


def message_generator(dependencies, specification, task, tasks_results):
    """Generate message with task information.

    Args:
        dependencies: List of dependency names.
        specification: Task specification.
        task: Task name.
        tasks_results: Dictionary of task results.

    Returns:
        Formatted message string.
    """
    result = f"TASK: {task}, SPECIFICATION: {specification}"
    for dep in dependencies:
        result += f", {dep}: {tasks_results[dep]}"
    return result


def get_real_docs(symbol_list):
    """Get real documentation for Python symbols.

    Args:
        symbol_list: List of symbol strings (e.g., "os.path.join").

    Returns:
        Documentation string for all symbols.
    """
    docs = ""
    for symbol in symbol_list:
        try:
            # 1. Dynamiczny import
            parts = symbol.split(".")
            module_name = parts[0]

            try:
                module = importlib.import_module(module_name)
            except ImportError:
                docs += f"--- ERROR: Could not import module {module_name} ---\n"
                continue

            # 2. Nawigacja do obiektu
            obj = module
            for part in parts[1:]:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    docs += f"--- ERROR: {symbol} not found ---\n"
                    obj = None
                    break

            if obj is None:
                continue

            docs += f"--- DOCUMENTATION FOR: {symbol} ---\n"

            # --- PRZYPADEK A: TO JEST MODUŁ (np. PyQt6.QtWidgets) ---
            if isinstance(obj, types.ModuleType):
                docs += "Type: Module\n"
                # Wypiszmy kluczowe klasy dostępne w module
                # (limitujemy ilość żeby nie zapchać contextu)
                attributes = [attr for attr in dir(obj) if not attr.startswith("_")]
                # Filtrujemy tylko klasy, żeby odsiać śmieci
                classes = [
                    attr for attr in attributes if isinstance(getattr(obj, attr), type)
                ]

                preview = ", ".join(classes[:50])  # Pierwsze 50 klas
                docs += f"Available Classes (Preview): {preview}...\n"
                if len(classes) > 50:
                    docs += f"(...and {len(classes) - 50} more)\n"

            # --- PRZYPADEK B: TO JEST KLASA LUB FUNKCJA ---
            else:
                # 1. Próba pobrania sygnatury (działa dla czystego Pythona)
                try:
                    sig = inspect.signature(obj)
                    docs += f"Signature: {symbol}{sig}\n"
                except (ValueError, TypeError):
                    # Fallback dla C-extensions
                    # (PyQt często ma sygnaturę w pierwszej linii docstringa)
                    pass

                # 2. Docstring (Najważniejsze dla PyQt)
                if obj.__doc__:
                    docs += f"Docstring:\n{obj.__doc__[:2000]}\n"  # Zwiększamy limit
                else:
                    # Ostatnia deska ratunku - help() capture
                    pass

            docs += "\n" + "=" * 30 + "\n"

        except Exception as e:
            docs += f"--- ERROR analyzing {symbol}: {str(e)} ---\n"

    return docs


def get_tag_content(tag, response_text):
    """Extract content between XML-style tags.

    Args:
        tag: Tag name to extract.
        response_text: Text containing the tags.

    Returns:
        Content between tags, or empty string if not found.
    """
    response_text = response_text.strip()
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start_index = response_text.find(start_tag)
    if start_index == -1:
        return ""
    end_index = response_text.find(end_tag, start_index + len(start_tag))
    if end_index == -1:
        return ""
    return response_text[start_index + len(start_tag) : end_index]


def export_file(string, file_name):
    """Export string to a file.

    Args:
        string: Content to write.
        file_name: Path to the file.
    """
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(string)


def export_specs(response_text):
    """Export specifications from response text.

    Args:
        response_text: Text containing FINALDOCS tag.
    """
    export_file(get_tag_content("FINALDOCS", response_text), "spec.md")
