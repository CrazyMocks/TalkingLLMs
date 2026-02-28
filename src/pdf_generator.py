import os
import json
import tempfile
from datetime import datetime
from pathlib import Path

from message import Message

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
    
    .metrics {{
      background: #128c7e;
      color: white;
      padding: 15px 20px;
      font-size: 0.9em;
    }}
    
    .metrics p {{
      margin: 5px 0;
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
    
    .message.left {{
      align-self: flex-start;
      background: #ffffff;
      border-top-left-radius: 0;
    }}
    
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
    
    .system-prompts {{
      background: #25d366;
      color: white;
      padding: 15px 20px;
    }}
    
    .system-prompts h2 {{
      margin: 0 0 10px 0;
      font-size: 1.1em;
    }}
    
    .system-prompt {{
      background: rgba(255, 255, 255, 0.15);
      padding: 10px 15px;
      border-radius: 8px;
      margin-bottom: 10px;
    }}
    
    .system-prompt:last-child {{
      margin-bottom: 0;
    }}
    
    .system-prompt .name {{
      font-weight: 600;
      margin-bottom: 5px;
      font-size: 0.9em;
    }}
    
    .system-prompt .content {{
      font-size: 0.85em;
      line-height: 1.4;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{title}</h1>
    <p>{timestamp}</p>
  </div>
  <div class="metrics">
    <p><strong>Num of messages:</strong> {num_of_messages}</p> 
    <p><strong>Model {nameA}:</strong> {modelA}</p> 
    <p><strong>Model {nameB}:</strong> {modelB}</p>
  </div>
  <div class="system-prompts">
    <h2>System Prompts</h2>
    <div class="system-prompt">
      <div class="name">{nameA}</div>
      <div class="content">{system_prompt_a}</div>
    </div>
    <div class="system-prompt">
      <div class="name">{nameB}</div>
      <div class="content">{system_prompt_b}</div>
    </div>
  </div>
  <div class="chat" id="chat"></div>
  <script>
    function escapeHtml(text) {{
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }}
    
    const messages = {messages_data};
    const chatContainer = document.getElementById('chat');
    
    messages.forEach(msg => {{
      const div = document.createElement('div');
      div.className = 'message ' + msg.side;
      div.innerHTML = '<div class="sender">' + escapeHtml(msg.sender) + '</div>' + marked.parse(msg.content);
      chatContainer.appendChild(div);
    }});
  </script>
</body>
</html>"""


def generate_pdf(
    messages: list[tuple[Message, str]],
    output_path: str,
    name1: str,
    name2: str,
    model1: str,
    model2: str,
    system_prompt1: str = "",
    system_prompt2: str = "",
    style: str = "whatsapp",
) -> None:
    """Generate a PDF from messages using Playwright and HTML."""
    
    # Tworzymy czystą strukturę danych i zrzucamy do JSON-a
    formatted_messages = []
    for message, sender in messages:
        side = "left" if sender == name1 else "right"
        formatted_messages.append({
            "sender": sender,
            "content": message.get_content() or "",
            "side": side
        })
    
    messages_json = json.dumps(formatted_messages)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = f"Chat between {name1} and {name2}"
    
    # Podstawiamy dane pod odpowiednie klucze
    html_content = HTML_TEMPLATE.format(
        title=title,
        timestamp=timestamp,
        messages_data=messages_json,
        num_of_messages=len(messages),
        nameA=name1,
        nameB=name2,
        modelA=model1,
        modelB=model2,
        system_prompt_a=system_prompt1 or "Brak system promptu",
        system_prompt_b=system_prompt2 or "Brak system promptu",
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
