import os
import tempfile
from datetime import datetime
from pathlib import Path

from .message import Message


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Chat Export</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    * {{
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}
    
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #e5ddd5;
    }}
    
    .header {{
      background: #075e54;
      color: white;
      padding: 15px 20px;
      text-align: center;
    }}
    
    .header h1 {{
      margin: 0;
      font-size: 1.4em;
    }}
    
    .header p {{
      margin: 5px 0 0 0;
      font-size: 0.85em;
      opacity: 0.8;
    }}
    
    .chat {{
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    
    .message {{
      max-width: 70%;
      padding: 10px 14px;
      border-radius: 12px;
      line-height: 1.5;
      word-wrap: break-word;
      font-size: 14px;
    }}
    
    /* Markdown styling */
    .message h1, .message h2, .message h3 {{
      margin: 0.5em 0 0.3em 0;
      font-weight: 600;
    }}
    
    .message h1 {{ font-size: 1.4em; }}
    .message h2 {{ font-size: 1.2em; }}
    .message h3 {{ font-size: 1.1em; }}
    
    .message p {{ margin: 0.5em 0; }}
    .message p:first-child {{ margin-top: 0; }}
    .message p:last-child {{ margin-bottom: 0; }}
    
    .message strong {{ font-weight: 600; }}
    .message em {{ font-style: italic; }}
    
    .message code {{
      background: rgba(0, 0, 0, 0.1);
      padding: 2px 5px;
      border-radius: 3px;
      font-family: 'Monaco', 'Consolas', monospace;
      font-size: 0.9em;
    }}
    
    .message pre {{
      background: rgba(0, 0, 0, 0.1);
      padding: 10px;
      border-radius: 6px;
      overflow-x: auto;
      margin: 0.5em 0;
    }}
    
    .message pre code {{
      background: none;
      padding: 0;
    }}
    
    .message ul, .message ol {{
      margin: 0.5em 0;
      padding-left: 1.5em;
    }}
    
    .message li {{ margin: 0.2em 0; }}
    
    .message a {{
      color: #0066cc;
      text-decoration: none;
    }}
    
    /* Left side (name1) */
    .message.left {{
      align-self: flex-start;
      background: #ffffff;
      border-top-left-radius: 0;
    }}
    
    /* Right side (name2) */
    .message.right {{
      align-self: flex-end;
      background: #dcf8c6;
      border-top-right-radius: 0;
    }}
    
    .message .sender {{
      font-size: 0.75em;
      font-weight: 600;
      margin-bottom: 4px;
      opacity: 0.7;
    }}
    
    .message.left .sender {{
      color: #075e54;
    }}
    
    .message.right .sender {{
      color: #128c7e;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{title}</h1>
    <p>{timestamp}</p>
  </div>
  <div class="chat" id="chat">
{messages}
  </div>
  <script>
    function escapeHtml(text) {{
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }}
    
    const messages = {messages_json};
    messages.forEach(msg => {{
      const div = document.createElement('div');
      div.className = 'message ' + msg.side;
      div.innerHTML = '<div class="sender">' + escapeHtml(msg.sender) + '</div>' + marked.parse(msg.content);
      document.getElementById('chat').appendChild(div);
    }});
  </script>
</body>
</html>"""


def generate_pdf(
    messages: list[tuple[Message, str]],
    output_path: str,
    name1: str,
    name2: str,
    style: str = "whatsapp",
) -> None:
    """Generate a PDF from messages using Playwright and HTML.
    
    Args:
        messages: List of (Message, sender_name) tuples
        output_path: Path to save the PDF
        name1: Name of the first agent
        name2: Name of the second agent
        style: Style to use (currently only 'whatsapp' is supported)
    """
    messages_json = []
    for message, sender in messages:
        side = "left" if sender == name1 else "right"
        content = message.get_content() or ""
        content = content.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        messages_json.append(f'{{"sender": "{sender}", "content": "{content}", "side": "{side}"}}')
    
    messages_html = ",".join(messages_json)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = f"Chat between {name1} and {name2}"
    
    html_content = HTML_TEMPLATE.format(
        title=title,
        timestamp=timestamp,
        messages=f"[{messages_html}]",
    )
    
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as html_file:
        html_file.write(html_content)
        html_path = html_file.name
    
    try:
        _convert_html_to_pdf(html_path, output_path)
    finally:
        if os.path.exists(html_path):
            os.remove(html_path)


def _convert_html_to_pdf(html_path: str, output_path: str) -> None:
    """Convert HTML to PDF using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError(
            "playwright is required for PDF generation. Install it with: pip install playwright && playwright install chromium"
        )
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(f"file://{html_path}", wait_until="networkidle")
        
        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "0.5cm", "right": "0.5cm", "bottom": "0.5cm", "left": "0.5cm"},
        )
        
        browser.close()