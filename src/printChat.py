import os
import time
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from playwright.sync_api import sync_playwright

# KONFIGURACJA
HTML_FILENAME = "chat.html"  # Nazwa twojego pliku
PDF_OUTPUT = "Chat_Export.pdf"
PORT = 8080


def start_server():
    """Uruchamia prosty serwer HTTP w tle, aby ominąć blokadę CORS."""
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(("", PORT), handler)
    print(f"[SENTINEL] Serwer lokalny uruchomiony na porcie {PORT}")
    httpd.serve_forever()


def generate_pdf():
    # 1. Uruchomienie serwera w tle
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Czas na rozruch

    with sync_playwright() as p:
        print("[SENTINEL] Uruchamianie silnika Chromium...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 2. Otwarcie strony
        local_url = f"http://localhost:{PORT}/{HTML_FILENAME}"
        print(f"[SENTINEL] Renderowanie strony: {local_url}")
        page.goto(local_url)

        # 3. Czekamy na załadowanie treści
        try:
            page.wait_for_selector(".message", timeout=5000)
        except:
            print("[SENTINEL] OSTRZEŻENIE: Nie wykryto wiadomości.")

        # 4. WSTRZYKIWANIE CSS - WERSJA POPRAWIONA (High Fidelity)
        print("[SENTINEL] Aplikowanie stylów druku (wymuszanie tła)...")

        css_injection = """
            /* 1. Ukrywamy panel boczny */
            .controls { display: none !important; }
            
            /* 2. Resetujemy układ strony dla PDF */
            html, body {
                height: auto !important;
                overflow: visible !important;
                margin: 0 !important;
                width: 100% !important;
            }
            
            /* 3. WYMUSZENIE DRUKOWANIA KOLORÓW I TŁA */
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }

            /* 4. Rozciągnięcie czatu */
            .chat-container {
                height: auto !important;
                display: block !important;
                width: 100% !important;
            }
            
            .chat {
                max-width: 100% !important;
                width: 100% !important;
                padding: 20px !important;
                margin: 0 !important;
                overflow: visible !important;
            }
        """

        page.add_style_tag(content=css_injection)

        # 5. Generowanie PDF z opcją print_background=True
        print(f"[SENTINEL] Zapisywanie PDF: {PDF_OUTPUT}")
        page.pdf(
            path=PDF_OUTPUT,
            format="A4",
            print_background=True,  # KLUCZOWE: Włącza renderowanie tła
            margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
        )

        browser.close()
        print("[SENTINEL] Dokument wygenerowany poprawnie.")


if __name__ == "__main__":
    # Sprawdzenie czy pliki istnieją w katalogu roboczym
    if not os.path.exists(HTML_FILENAME):
        print(
            f"[SENTINEL] BŁĄD: Nie znaleziono pliku {HTML_FILENAME} w bieżącym katalogu."
        )
    else:
        generate_pdf()
