import os
import sys

# --- SENTINEL HOTFIX START ---
# Wymuszenie ścieżek dla macOS Apple Silicon / Intel
if sys.platform == "darwin":
    # Ścieżki gdzie Homebrew trzyma biblioteki (GObject, Pango, etc.)
    base_paths = [
        "/opt/homebrew/lib",  # Apple Silicon
        "/usr/local/lib",  # Intel Mac
        "/opt/homebrew/opt/glib/lib",
        "/opt/homebrew/opt/pango/lib",
        "/opt/homebrew/opt/harfbuzz/lib",
    ]

    # Budowanie ścieżki dla linkera
    current_path = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    new_path = ":".join(base_paths) + ":" + current_path

    # Wstrzyknięcie do zmiennych środowiskowych procesu
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = new_path
# --- SENTINEL HOTFIX END ---
import markdown
import re
from weasyprint import HTML, CSS
from datetime import datetime


class SentinelDocGenerator:
    def __init__(self):
        self.css_styles = """
            @page {
                size: A4;
                margin: 2.5cm;
                @bottom-right {
                    content: "Strona " counter(page);
                    font-size: 9pt;
                    color: #666;
                }
                @bottom-left {
                    content: "SENTINEL AUDIT REPORT";
                    font-size: 9pt;
                    color: #666;
                }
            }
            body {
                font-family: 'Roboto', 'Helvetica', sans-serif;
                line-height: 1.6;
                color: #333;
                font-size: 11pt;
            }
            h1 {
                font-size: 24pt;
                color: #2c3e50;
                border-bottom: 2px solid #2c3e50;
                padding-bottom: 10px;
                margin-top: 0;
            }
            h2 {
                font-size: 16pt;
                color: #e74c3c; /* Sentinel Red */
                margin-top: 25px;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-left: 5px solid #e74c3c;
                padding-left: 10px;
            }
            ul {
                list-style-type: square;
            }
            li {
                margin-bottom: 5px;
            }
            code {
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Consolas', monospace;
                color: #c7254e;
            }
            blockquote {
                background: #f9f9f9;
                border-left: 10px solid #ccc;
                margin: 1.5em 10px;
                padding: 0.5em 10px;
                font-style: italic;
            }
            .meta-info {
                font-size: 0.8em;
                color: #7f8c8d;
                margin-bottom: 30px;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }
        """

    def _normalize_tags(self, text):
        """
        Zamienia pseudo-tagi XML na Markdown H2 dla czytelności.
        """
        # Mapowanie tagów na ludzkie nagłówki
        tag_map = {
            r"<system_role>": "## Rola Systemowa",
            r"</system_role>": "",
            r"<personality>": "## Profil Osobowości",
            r"</personality>": "",
            r"<objectives>": "## Cele Operacyjne",
            r"</objectives>": "",
            r"<interaction_rules>": "## Zasady Interakcji",
            r"</interaction_rules>": "",
        }

        normalized_text = text
        for pattern, replacement in tag_map.items():
            normalized_text = re.sub(
                pattern, replacement, normalized_text, flags=re.IGNORECASE
            )

        return normalized_text.strip()

    def generate(self, raw_text, output_filename="Sentinel_Report.pdf"):
        # remove file if exists
        if os.path.exists(output_filename):
            os.remove(output_filename)
        # 1. Pre-processing
        markdown_text = self._normalize_tags(raw_text)

        # 2. Dodanie nagłówka dokumentu
        typeOfAgent = "SENTINEL" if "Sentinel" in output_filename else "CANVAS"
        header = f"# Specyfikacja Agenta {typeOfAgent}\n\n"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meta = f"<div class='meta-info'>Generated: {timestamp} | Classification: INTERNAL</div>\n\n"

        full_markdown = header + meta + markdown_text

        # 3. Konwersja Markdown -> HTML
        html_content = markdown.markdown(full_markdown)

        # 4. Renderowanie PDF
        print(f"[{typeOfAgent}] Generowanie pliku: {output_filename}...")
        try:
            HTML(string=html_content).write_pdf(
                output_filename, stylesheets=[CSS(string=self.css_styles)]
            )
            print(f"[{typeOfAgent}] SUKCES. Dokument gotowy do druku.")
        except Exception as e:
            print(f"[{typeOfAgent}] BŁĄD KRYTYCZNY: {e}")
            print("Sprawdź, czy masz zainstalowane biblioteki GTK (dla WeasyPrint).")


# --- EXECUTION BLOCK ---

if __name__ == "__main__":
    raw_input = ""
    with open(sys.argv[1], "r") as f:
        raw_input = f.read()
    generator = SentinelDocGenerator()
    generator.generate(raw_input, output_filename=sys.argv[1].replace(".txt", ".pdf"))
