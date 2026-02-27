from message import Message
import os
import importlib
import inspect
import json
import re

def clear_files():
    with open("messagesA", "w") as f:
        f.write("")
    with open("messagesB", "w") as f:
        f.write("")
def save_message_to_file(message,file):
    with open(file, "a") as f:
        f.write(message)
        f.write(f"\n{sep}\n")
def export_messages(messages,sep=''):
    current_agent = "A"
    for message in messages:
        if current_agent == 'A':
            save_message_to_file(message, "messagesA")
        else:
            save_message_to_file(message, "messagesB")
        current_agent = "B" if current_agent == "A" else "A"
def load_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        txt = f.read()
    return txt
def load_initial_message(initial_message_file, project_discription):
    projDesc = ""
    if os.path.exists(project_discription):
        projDesc = load_file(project_discription)
    else:
        projDesc = project_discription
    template = load_file(initial_message_file)
    return Message("user", template.replace("<Project Description>",projDesc))
def refresh_chat(conv):
    clear_files()
    export_messages(conv.get_messages(),sep=sep)

def parse_and_save_files(response_text, output_dir="project_root"):
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
            
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"--> Utworzono: {full_path}")
def get_last_sentence(text):
    sentences = text.split(".")
    return ''.join(sentences[-5:])
def messageGenerator(dependencies, specification, task, tasksResults):
    result = f"TASK: {task}, SPECIFICATION: {specification}"
    for dep in dependencies:
        result+=f", {dep}: {tasksResults[dep]}"
    return result
def get_real_docs(symbol_list):
    docs = ""
    for symbol in symbol_list:
        try:
            # 1. Dynamiczny import
            parts = symbol.split('.')
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
            
            if obj is None: continue

            docs += f"--- DOCUMENTATION FOR: {symbol} ---\n"
            
            # --- PRZYPADEK A: TO JEST MODUŁ (np. PyQt6.QtWidgets) ---
            if isinstance(obj, types.ModuleType):
                docs += "Type: Module\n"
                # Wypiszmy kluczowe klasy dostępne w module (limitujemy ilość żeby nie zapchać contextu)
                attributes = [attr for attr in dir(obj) if not attr.startswith('_')]
                # Filtrujemy tylko klasy, żeby odsiać śmieci
                classes = [attr for attr in attributes if isinstance(getattr(obj, attr), type)]
                
                preview = ", ".join(classes[:50]) # Pierwsze 50 klas
                docs += f"Available Classes (Preview): {preview}...\n"
                if len(classes) > 50:
                    docs += f"(...and {len(classes)-50} more)\n"
            
            # --- PRZYPADEK B: TO JEST KLASA LUB FUNKCJA ---
            else:
                # 1. Próba pobrania sygnatury (działa dla czystego Pythona)
                try:
                    sig = inspect.signature(obj)
                    docs += f"Signature: {symbol}{sig}\n"
                except (ValueError, TypeError):
                    # Fallback dla C-extensions (PyQt często ma sygnaturę w pierwszej linii docstringa)
                    pass

                # 2. Docstring (Najważniejsze dla PyQt)
                if obj.__doc__:
                    docs += f"Docstring:\n{obj.__doc__[:2000]}\n" # Zwiększamy limit znaków
                else:
                    # Ostatnia deska ratunku - help() capture (brzydkie ale skuteczne)
                    pass 
            
            docs += "\n" + "="*30 + "\n"

        except Exception as e:
            docs += f"--- ERROR analyzing {symbol}: {str(e)} ---\n"
    
    return docs
def get_tag_content(tag, response_text):
    response_text = response_text.strip()
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    start_index = response_text.find(start_tag)
    end_index = response_text.rfind(end_tag)
    if start_index == -1 or end_index == -1 or start_index >= end_index:
        return ""
    return response_text[start_index + len(start_tag):end_index]
def export_file(string, file_name):
    with open(file_name, "w",encoding='utf-8') as f:
        f.write(string)
def export_specs(response_text):
    export_file(get_tag_content("FINALDOCS", response_text), "spec.md")