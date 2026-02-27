def list_files(directory):
    """
    List all files in a directory.

    Args:
        directory: The directory to list files in.

    Returns:
        A list of all files in the directory.
    """
    return os.listdir(directory)

def read_file(file_path):
    """
    Read the contents of a file.

    Args:
        file_path: The path to the file to read.

    Returns:
        The contents of the file.
    """
    with open(file_path, "r") as f:
        return f.read()

def write_file(file_path, contents):
    """
    Write the contents of a file.

    Args:
        file_path: The path to the file to write.
        contents: The contents of the file.
    """
    with open(file_path, "w") as f:
        f.write(contents)

def create_directory(directory):
    """
    Create a directory.

    Args:
        directory: The directory to create.
    """
    os.makedirs(directory, exist_ok=True)

def execute_command(command):
    """
    Execute a command after user confirmation.

    Args:
        command: The command to execute.
    """
    flag = input(f"Executing command: {command} (y/n): ")
    if flag == "y" or flag == "Y" or flag == "yes" or flag == "Yes" or flag == "YES" or flag == "":
        try:
            return os.system(command)
        except Exception as e:
            return str(e)
    else:
        return "Command not executed"



tools = [
  {
    "type": "function",
    "function": {
      "name": "search_gutenberg_books",
      "description": "Search for books in the Project Gutenberg library based on specified search terms",
      "parameters": {
        "type": "object",
        "properties": {
          "search_terms": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "List of search terms to find books in the Gutenberg library (e.g. ['dickens', 'great'] to search for books by Dickens with 'great' in the title)"
          }
        },
        "required": ["search_terms"]
      }
    }
  }
]

TOOL_MAPPING = {
    "search_gutenberg_books": search_gutenberg_books
}

